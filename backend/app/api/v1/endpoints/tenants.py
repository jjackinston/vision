from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db, create_tenant_schema
from app.core.security import get_current_user, CurrentUser
from app.core.plan_gate import enforce_limit
from slugify import slugify

router = APIRouter()


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
    from sqlalchemy import select
    from app.models.tenant import TenantMember
    result = await db.execute(
        select(TenantMember).where(TenantMember.tenant_id == user.tenant_id)
    )
    return result.scalars().all()


@router.post("/current/invite")
async def invite_member(
    email: str,
    role: str = "analyst",
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    user.require("admin")

    # Enforce team member plan limit before sending invite
    from app.models.tenant import TenantMember
    current_members = await db.scalar(
        select(func.count(TenantMember.id)).where(TenantMember.tenant_id == user.tenant_id)
    ) or 0
    await enforce_limit(db, user.tenant_id, "users", current_members)

    # In production: send invite email via Clerk
    return {"invited": email, "role": role, "status": "invitation_sent"}


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
