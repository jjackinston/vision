from typing import Optional, Dict, Any
import hashlib
import secrets
import jwt
import httpx
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db

security = HTTPBearer(auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_clerk_token(token: str) -> Dict[str, Any]:
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://api.clerk.com/v1/jwks",
                headers={"Authorization": f"Bearer {settings.CLERK_SECRET_KEY}"}
            )
        jwks = resp.json()
        header = jwt.get_unverified_header(token)
        public_key = next(
            (k for k in jwks["keys"] if k["kid"] == header["kid"]),
            None
        )
        if not public_key:
            raise HTTPException(status_code=401, detail="Invalid token key")
        payload = jwt.decode(
            token,
            jwt.algorithms.RSAAlgorithm.from_jwk(public_key),
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_aud": False},
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")


def hash_api_key(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()


def generate_api_key() -> tuple[str, str, str]:
    raw = f"sv_{secrets.token_urlsafe(32)}"
    prefix = raw[:12]
    hashed = hash_api_key(raw)
    return raw, prefix, hashed


class CurrentUser:
    def __init__(self, user_id: str, tenant_id: str, role: str, tenant_slug: str):
        self.user_id = user_id
        self.tenant_id = tenant_id
        self.role = role
        self.tenant_slug = tenant_slug

    def can(self, action: str) -> bool:
        permissions = {
            "owner": {"read", "write", "delete", "admin", "billing"},
            "admin": {"read", "write", "delete", "admin"},
            "manager": {"read", "write"},
            "analyst": {"read", "write"},
            "viewer": {"read"},
        }
        return action in permissions.get(self.role, set())

    def require(self, action: str) -> None:
        if not self.can(action):
            raise HTTPException(status_code=403, detail=f"Permission denied: {action}")


async def _get_dev_user(db: AsyncSession) -> "CurrentUser":
    """Return the first seeded user+tenant for local dev (no Clerk configured)."""
    from sqlalchemy import select
    from app.models.user import User
    from app.models.tenant import Tenant, TenantMember

    result = await db.execute(select(User).where(User.is_active == True).limit(1))
    user = result.scalar_one_or_none()
    if not user:
        return CurrentUser(user_id="dev-user", tenant_id="dev-tenant", role="owner", tenant_slug="demo")

    result2 = await db.execute(
        select(TenantMember, Tenant)
        .join(Tenant, TenantMember.tenant_id == Tenant.id)
        .where(TenantMember.user_id == user.id)
        .limit(1)
    )
    row = result2.first()
    if not row:
        return CurrentUser(user_id=str(user.id), tenant_id="dev-tenant", role="owner", tenant_slug="demo")

    member, tenant = row
    return CurrentUser(
        user_id=str(user.id),
        tenant_id=str(tenant.id),
        role=member.role,
        tenant_slug=tenant.slug,
    )


def require_subscription():
    """
    Returns a FastAPI dependency that checks the current user's tenant is active
    and that their trial has not expired without a paid subscription.

    Usage:
        user: CurrentUser = Depends(require_subscription())
    """
    async def _dep(
        credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
        db: AsyncSession = Depends(get_db),
    ) -> CurrentUser:
        current_user = await get_current_user(credentials, db)

        # Delegate to plan_gate for consistent expiry + past-due logic
        from app.core.plan_gate import _assert_subscription_active
        await _assert_subscription_active(db, current_user.tenant_id)

        return current_user

    return _dep


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
    db: AsyncSession = Depends(get_db),
) -> CurrentUser:
    # Dev bypass: when Clerk is not configured, use the seeded demo user
    if not settings.CLERK_SECRET_KEY:
        return await _get_dev_user(db)

    if not credentials:
        raise HTTPException(status_code=401, detail="Authorization required")

    from sqlalchemy import select
    from app.models.user import User
    from app.models.tenant import Tenant, TenantMember
    from app.services.user_service import get_user_by_clerk_id

    payload = await verify_clerk_token(credentials.credentials)
    clerk_id = payload.get("sub")
    user = await get_user_by_clerk_id(db, clerk_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found — sign in again to provision account")

    # Resolve tenant: Clerk Orgs set org_id; solo users fall back to their first membership
    org_id = payload.get("org_id") or (payload.get("metadata") or {}).get("tenant_id")
    if org_id:
        result = await db.execute(
            select(TenantMember, Tenant)
            .join(Tenant, TenantMember.tenant_id == Tenant.id)
            .where(TenantMember.user_id == user.id, TenantMember.tenant_id == org_id)
            .limit(1)
        )
    else:
        # Solo user (no Clerk Org) — use their auto-provisioned tenant
        result = await db.execute(
            select(TenantMember, Tenant)
            .join(Tenant, TenantMember.tenant_id == Tenant.id)
            .where(TenantMember.user_id == user.id)
            .order_by(TenantMember.joined_at)
            .limit(1)
        )

    row = result.first()
    if not row:
        raise HTTPException(status_code=403, detail="No tenant membership found — account provisioning may be incomplete")

    member, tenant = row
    return CurrentUser(
        user_id=str(user.id),
        tenant_id=str(tenant.id),
        role=member.role,
        tenant_slug=tenant.slug,
    )
