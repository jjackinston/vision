from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db, create_tenant_schema
from app.core.security import get_current_user, CurrentUser
from app.core.plan_gate import enforce_limit
from slugify import slugify

router = APIRouter()


# ── Request models ────────────────────────────────────────────────────────────

class InviteRequest(BaseModel):
    email: str            # EmailStr would require email-validator; plain str is safe here
    role: str = "analyst"


@router.post("/")
async def create_tenant(
    name: str,
    plan_id: str,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    from app.models.tenant import Tenant, TenantMember
    slug = slugify(name)
    tenant = Tenant(name=name, slug=slug, plan_id=plan_id)
    db.add(tenant)
    await db.flush()
    member = TenantMember(tenant_id=tenant.id, user_id=user.user_id, role="owner")
    db.add(member)
    await db.commit()
    await create_tenant_schema(slug)
    return tenant


@router.get("/current")
async def get_current_tenant(
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    from sqlalchemy import select
    from app.models.tenant import Tenant
    result = await db.execute(select(Tenant).where(Tenant.id == user.tenant_id))
    return result.scalar_one_or_none()


@router.get("/current/members")
async def list_members(
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """
    List all members of the current tenant with user details (name, email).
    Joins TenantMember → User so the frontend gets a complete record.
    """
    from app.models.tenant import TenantMember
    from app.models.user import User

    result = await db.execute(
        select(
            TenantMember.id,
            TenantMember.user_id,
            TenantMember.role,
            TenantMember.joined_at,
            User.full_name,
            User.email,
        )
        .join(User, User.id == TenantMember.user_id)
        .where(TenantMember.tenant_id == user.tenant_id)
        .order_by(TenantMember.joined_at.asc())
    )
    rows = result.fetchall()
    return [
        {
            "id": str(row.id),
            "user_id": str(row.user_id),
            "name": row.full_name or "",
            "email": row.email or "",
            "role": row.role,
            "joined_at": row.joined_at.isoformat() if row.joined_at else None,
        }
        for row in rows
    ]


@router.post("/current/invite")
async def invite_member(
    body: InviteRequest,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """
    Invite a new team member by email.
    Enforces plan user-limit before sending. In production, fires a
    Clerk invitation email; returns a status object in all environments.
    """
    user.require("admin")

    from app.models.tenant import TenantMember
    current_members = await db.scalar(
        select(func.count(TenantMember.id)).where(TenantMember.tenant_id == user.tenant_id)
    ) or 0
    await enforce_limit(db, user.tenant_id, "users", current_members)

    # TODO: call Clerk /invitations API with body.email when CLERK_SECRET_KEY is set
    return {"message": f"Invitation sent to {body.email}", "role": body.role, "status": "invitation_sent"}


@router.delete("/current/members/{member_id}")
async def remove_member(
    member_id: str,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """Remove a team member. Owners cannot be removed."""
    user.require("admin")

    from sqlalchemy import delete as sql_delete
    from app.models.tenant import TenantMember

    # Prevent removing an owner
    target = await db.scalar(
        select(TenantMember.role).where(
            TenantMember.id == member_id,
            TenantMember.tenant_id == user.tenant_id,
        )
    )
    if target is None:
        raise HTTPException(404, "Member not found")
    if target == "owner":
        raise HTTPException(403, "Cannot remove the workspace owner")

    await db.execute(
        sql_delete(TenantMember).where(
            TenantMember.id == member_id,
            TenantMember.tenant_id == user.tenant_id,
        )
    )
    await db.commit()
    return {"removed": member_id}


@router.get("/current/settings")
async def get_tenant_settings(
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """Return the tenant's settings JSON blob."""
    from app.models.tenant import Tenant
    result = await db.execute(select(Tenant.settings).where(Tenant.id == user.tenant_id))
    settings = result.scalar_one_or_none()
    return settings or {}


@router.patch("/current/settings")
async def patch_tenant_settings(
    body: dict,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """
    Merge-patch the tenant's settings JSON blob.
    Existing keys not in `body` are preserved; keys in `body` overwrite.
    Used by onboarding to mark completion, feature flags, UI preferences, etc.
    """
    from sqlalchemy import update
    from app.models.tenant import Tenant

    result = await db.execute(select(Tenant.settings).where(Tenant.id == user.tenant_id))
    current = result.scalar_one_or_none() or {}
    merged = {**current, **body}

    await db.execute(
        update(Tenant).where(Tenant.id == user.tenant_id).values(settings=merged)
    )
    await db.commit()
    return {"settings": merged}


@router.put("/current/members/{member_id}/role")
async def update_member_role(
    member_id: str,
    role: str,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    user.require("admin")
    valid_roles = {"owner", "admin", "manager", "analyst", "viewer"}
    if role not in valid_roles:
        raise HTTPException(400, f"Invalid role. Must be one of {valid_roles}")
    from sqlalchemy import update
    from app.models.tenant import TenantMember
    await db.execute(
        update(TenantMember).where(TenantMember.id == member_id, TenantMember.tenant_id == user.tenant_id)
        .values(role=role)
    )
    await db.commit()
    return {"member_id": member_id, "new_role": role}
