from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_user, CurrentUser, generate_api_key

router = APIRouter()


# ── Request / Response models ─────────────────────────────────────────────────

class ApiKeyCreate(BaseModel):
    name: str
    scopes: list[str] = ["read", "write"]


# ─────────────────────────────────────────────────────────────────────────────

@router.get("/me")
async def get_me(user: CurrentUser = Depends(get_current_user)):
    return {"user_id": user.user_id, "tenant_id": user.tenant_id, "role": user.role}


@router.post("/api-keys")
async def create_api_key(
    body: ApiKeyCreate,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """
    Create a new API key.
    Returns the raw key **once** — it is never stored in plain text.
    """
    user.require("admin")
    raw, prefix, hashed = generate_api_key()
    from app.models.tenant import APIKey
    key_row = APIKey(
        tenant_id=user.tenant_id,
        user_id=user.user_id,
        name=body.name,
        key_hash=hashed,
        key_prefix=prefix,
        scopes=body.scopes,
    )
    db.add(key_row)
    await db.commit()
    await db.refresh(key_row)
    return {
        "id": str(key_row.id),
        "name": body.name,
        "prefix": prefix,
        "key": raw,               # one-time raw key
        "created_at": key_row.created_at.isoformat() if key_row.created_at else None,
        "warning": "Store this key — it won't be shown again.",
    }


@router.get("/api-keys")
async def list_api_keys(
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """List all active API keys for the current tenant (raw key never returned)."""
    from sqlalchemy import select
    from app.models.tenant import APIKey
    result = await db.execute(
        select(APIKey)
        .where(APIKey.tenant_id == user.tenant_id, APIKey.is_active == True)
        .order_by(APIKey.created_at.desc())
    )
    keys = result.scalars().all()
    return [
        {
            "id": str(k.id),
            "name": k.name,
            "prefix": k.key_prefix,       # frontend expects "prefix" not "key_prefix"
            "scopes": k.scopes or [],
            "created_at": k.created_at.isoformat() if k.created_at else None,
            "last_used_at": k.last_used_at.isoformat() if k.last_used_at else None,
        }
        for k in keys
    ]


@router.delete("/api-keys/{key_id}")
async def revoke_api_key(
    key_id: str,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """Revoke (soft-delete) an API key."""
    user.require("admin")
    from sqlalchemy import update
    from app.models.tenant import APIKey
    result = await db.execute(
        update(APIKey)
        .where(APIKey.id == key_id, APIKey.tenant_id == user.tenant_id)
        .values(is_active=False)
    )
    await db.commit()
    if result.rowcount == 0:
        raise HTTPException(404, "API key not found")
    return {"revoked": key_id}
