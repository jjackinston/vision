"""
SellerVision AI — Super-Admin API
==================================
All routes require the `X-Admin-Key` header matching ADMIN_SECRET_KEY in config.
These endpoints are NOT tenant-scoped — they have full cross-tenant visibility.

Routes:
  GET  /admin/stats          — system overview (tenants, users, revenue, plans)
  GET  /admin/tenants        — paginated tenant list with usage + plan
  GET  /admin/tenants/{id}   — single tenant detail
  PATCH /admin/tenants/{id}  — update tenant (plan, is_active, trial_ends_at)
  GET  /admin/users          — paginated user list
  GET  /admin/audit-logs     — recent audit log entries across all tenants
"""
import secrets
import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text, update

from app.core.config import settings
from app.core.database import get_db

router = APIRouter()
logger = logging.getLogger(__name__)


# ── Auth dependency ────────────────────────────────────────────────────
async def require_admin(x_admin_key: Optional[str] = Header(None, alias="X-Admin-Key")) -> None:
    """
    Validates the X-Admin-Key header.
    - If ADMIN_SECRET_KEY is empty → admin routes are disabled (503).
    - Uses constant-time comparison to prevent timing attacks.
    """
    if not settings.ADMIN_SECRET_KEY:
        raise HTTPException(status_code=503, detail="Admin panel is disabled (ADMIN_SECRET_KEY not set)")
    if not x_admin_key:
        raise HTTPException(status_code=401, detail="X-Admin-Key header required")
    if not secrets.compare_digest(x_admin_key, settings.ADMIN_SECRET_KEY):
        logger.warning("Invalid admin key attempt")
        raise HTTPException(status_code=403, detail="Invalid admin key")


# ── Pydantic models ────────────────────────────────────────────────────
class TenantPatch(BaseModel):
    is_active: Optional[bool] = None
    plan_name: Optional[str] = None          # "Starter" / "Professional" / "Business" / "Agency"
    trial_ends_at: Optional[datetime] = None
    notes: Optional[str] = None


# ── Helper: safe tenant row → dict ────────────────────────────────────
def _tenant_row(row) -> dict:
    # Row is (Tenant, Plan, member_count) — product_count removed (no tenant_id on products)
    tenant, plan, member_count = row
    return {
        "id":           str(tenant.id),
        "slug":         tenant.slug,
        "name":         tenant.name,
        "plan":         plan.name if plan else "Free",
        "plan_id":      str(plan.id) if plan else None,
        "is_active":    tenant.is_active,
        "trial_ends_at": tenant.trial_ends_at.isoformat() if tenant.trial_ends_at else None,
        "stripe_customer_id":     tenant.stripe_customer_id,
        "stripe_subscription_id": tenant.stripe_subscription_id,
        "member_count":  int(member_count or 0),
        "product_count": 0,  # products don't have a tenant_id column in this schema
        "created_at":   tenant.created_at.isoformat() if hasattr(tenant, "created_at") and tenant.created_at else None,
    }


# ── GET /admin/stats ───────────────────────────────────────────────────
@router.get("/stats", dependencies=[Depends(require_admin)])
async def get_stats(db: AsyncSession = Depends(get_db)):
    """System-wide KPIs for the ops dashboard."""
    from app.models.tenant import Tenant, Plan, TenantMember
    from app.models.user import User
    from app.models.product import Product

    total_tenants = await db.scalar(select(func.count(Tenant.id)))
    active_tenants = await db.scalar(select(func.count(Tenant.id)).where(Tenant.is_active == True))
    total_users    = await db.scalar(select(func.count(User.id)).where(User.is_active == True))
    total_products = await db.scalar(select(func.count(Product.id)))

    # Plan distribution
    plan_dist_result = await db.execute(
        select(Plan.name, func.count(Tenant.id).label("count"))
        .join(Tenant, Tenant.plan_id == Plan.id, isouter=True)
        .group_by(Plan.name)
        .order_by(func.count(Tenant.id).desc())
    )
    plan_distribution = {row.name: row.count for row in plan_dist_result}

    # Tenants with active Stripe subscriptions (paying customers)
    paying = await db.scalar(
        select(func.count(Tenant.id))
        .where(Tenant.stripe_subscription_id.isnot(None), Tenant.is_active == True)
    )

    # New tenants in last 30 days
    thirty_days_ago = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    new_tenants_30d_result = await db.execute(
        text("SELECT COUNT(*) FROM tenants WHERE created_at >= NOW() - INTERVAL '30 days'")
    )
    new_tenants_30d = new_tenants_30d_result.scalar() or 0

    return {
        "tenants": {
            "total":   int(total_tenants or 0),
            "active":  int(active_tenants or 0),
            "paying":  int(paying or 0),
            "new_30d": int(new_tenants_30d),
            "trial":   int((active_tenants or 0) - (paying or 0)),
        },
        "users": {
            "total": int(total_users or 0),
        },
        "products": {
            "total": int(total_products or 0),
        },
        "plan_distribution": plan_distribution,
    }


# ── GET /admin/tenants ─────────────────────────────────────────────────
@router.get("/tenants", dependencies=[Depends(require_admin)])
async def list_tenants(
    page: int = Query(1, ge=1),
    per_page: int = Query(25, ge=1, le=100),
    search: Optional[str] = Query(None),
    plan: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    from app.models.tenant import Tenant, Plan, TenantMember

    q = (
        select(
            Tenant,
            Plan,
            func.count(TenantMember.id).label("member_count"),
        )
        .join(Plan, Tenant.plan_id == Plan.id, isouter=True)
        .outerjoin(TenantMember, TenantMember.tenant_id == Tenant.id)
        .group_by(Tenant.id, Plan.id)
    )

    if search:
        q = q.where(
            Tenant.name.ilike(f"%{search}%") | Tenant.slug.ilike(f"%{search}%")
        )
    if plan:
        q = q.where(func.lower(Plan.name) == plan.lower())
    if is_active is not None:
        q = q.where(Tenant.is_active == is_active)

    # Total count
    count_q = select(func.count()).select_from(
        select(Tenant.id)
        .join(Plan, Tenant.plan_id == Plan.id, isouter=True)
        .where(
            *(
                [Tenant.name.ilike(f"%{search}%") | Tenant.slug.ilike(f"%{search}%")]
                if search else []
            ),
            *(([func.lower(Plan.name) == plan.lower()]) if plan else []),
            *(([Tenant.is_active == is_active]) if is_active is not None else []),
        )
        .subquery()
    )
    total = await db.scalar(count_q) or 0

    q = q.order_by(Tenant.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(q)
    rows = result.all()

    return {
        "items": [_tenant_row(r) for r in rows],
        "total": int(total),
        "page": page,
        "per_page": per_page,
    }


# ── GET /admin/tenants/{id} ────────────────────────────────────────────
@router.get("/tenants/{tenant_id}", dependencies=[Depends(require_admin)])
async def get_tenant(tenant_id: str, db: AsyncSession = Depends(get_db)):
    from app.models.tenant import Tenant, Plan, TenantMember
    from app.models.user import User

    result = await db.execute(
        select(Tenant, Plan)
        .join(Plan, Tenant.plan_id == Plan.id, isouter=True)
        .where(Tenant.id == tenant_id)
    )
    row = result.first()
    if not row:
        raise HTTPException(404, "Tenant not found")

    tenant, plan = row

    # Members with user info
    members_result = await db.execute(
        select(TenantMember, User)
        .join(User, TenantMember.user_id == User.id)
        .where(TenantMember.tenant_id == tenant.id)
        .order_by(TenantMember.joined_at)
    )
    members = [
        {
            "user_id":    str(m.user_id),
            "email":      u.email,
            "full_name":  u.full_name,
            "role":       m.role,
            "joined_at":  m.joined_at.isoformat() if m.joined_at else None,
        }
        for m, u in members_result.all()
    ]

    # Recent audit log entries
    audit_result = await db.execute(
        text("""
            SELECT action, resource_type, resource_id::text, created_at
            FROM audit_logs
            WHERE tenant_id = :tid
            ORDER BY created_at DESC
            LIMIT 20
        """),
        {"tid": str(tenant.id)},
    )
    audit_logs = [
        {"action": r[0], "resource_type": r[1], "resource_id": r[2],
         "created_at": r[3].isoformat() if r[3] else None}
        for r in audit_result.fetchall()
    ]

    return {
        "id":           str(tenant.id),
        "slug":         tenant.slug,
        "name":         tenant.name,
        "plan":         plan.name if plan else "Free",
        "is_active":    tenant.is_active,
        "trial_ends_at": tenant.trial_ends_at.isoformat() if tenant.trial_ends_at else None,
        "stripe_customer_id":     tenant.stripe_customer_id,
        "stripe_subscription_id": tenant.stripe_subscription_id,
        "settings":     tenant.settings or {},
        "members":      members,
        "recent_audit_logs": audit_logs,
        "created_at":   tenant.created_at.isoformat() if hasattr(tenant, "created_at") and tenant.created_at else None,
    }


# ── PATCH /admin/tenants/{id} ──────────────────────────────────────────
@router.patch("/tenants/{tenant_id}", dependencies=[Depends(require_admin)])
async def update_tenant(
    tenant_id: str,
    body: TenantPatch,
    db: AsyncSession = Depends(get_db),
):
    from app.models.tenant import Tenant, Plan

    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(404, "Tenant not found")

    updates: dict = {}
    if body.is_active is not None:
        updates["is_active"] = body.is_active
    if body.trial_ends_at is not None:
        updates["trial_ends_at"] = body.trial_ends_at
    if body.plan_name:
        plan_result = await db.execute(
            select(Plan).where(func.lower(Plan.name) == body.plan_name.lower())
        )
        plan = plan_result.scalar_one_or_none()
        if not plan:
            raise HTTPException(400, f"Unknown plan: {body.plan_name}")
        updates["plan_id"] = plan.id
    if body.notes is not None:
        current_settings = tenant.settings or {}
        current_settings["admin_notes"] = body.notes
        updates["settings"] = current_settings

    if updates:
        await db.execute(update(Tenant).where(Tenant.id == tenant_id).values(**updates))
        await db.commit()
        logger.info("Admin updated tenant %s: %s", tenant_id, list(updates.keys()))

    return {"updated": True, "fields": list(updates.keys())}


# ── GET /admin/users ───────────────────────────────────────────────────
@router.get("/users", dependencies=[Depends(require_admin)])
async def list_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(25, ge=1, le=100),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    from app.models.user import User
    from app.models.tenant import TenantMember, Tenant

    q = (
        select(User, TenantMember, Tenant)
        .outerjoin(TenantMember, TenantMember.user_id == User.id)
        .outerjoin(Tenant, TenantMember.tenant_id == Tenant.id)
    )
    if search:
        q = q.where(
            User.email.ilike(f"%{search}%") | User.full_name.ilike(f"%{search}%")
        )

    total = await db.scalar(
        select(func.count(User.id))
        .where(User.email.ilike(f"%{search}%") if search else True)
    ) or 0

    q = q.order_by(User.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(q)

    seen: set = set()
    items = []
    for user, member, tenant in result.all():
        if str(user.id) in seen:
            continue
        seen.add(str(user.id))
        items.append({
            "id":         str(user.id),
            "email":      user.email,
            "full_name":  user.full_name,
            "clerk_id":   user.clerk_id,
            "is_active":  user.is_active,
            "tenant":     tenant.slug if tenant else None,
            "tenant_id":  str(tenant.id) if tenant else None,
            "role":       member.role if member else None,
            "last_login": user.last_login_at.isoformat() if user.last_login_at else None,
            "created_at": user.created_at.isoformat() if hasattr(user, "created_at") and user.created_at else None,
        })

    return {"items": items, "total": int(total), "page": page, "per_page": per_page}


# ── GET /admin/audit-logs ──────────────────────────────────────────────
@router.get("/audit-logs", dependencies=[Depends(require_admin)])
async def list_audit_logs(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    tenant_id: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    filters = []
    params: dict = {"limit": per_page, "offset": (page - 1) * per_page}
    if tenant_id:
        filters.append("tenant_id = :tenant_id")
        params["tenant_id"] = tenant_id
    if action:
        filters.append("action ILIKE :action")
        params["action"] = f"%{action}%"

    where = ("WHERE " + " AND ".join(filters)) if filters else ""

    count_result = await db.execute(
        text(f"SELECT COUNT(*) FROM audit_logs {where}"),
        {k: v for k, v in params.items() if k not in ("limit", "offset")},
    )
    total = count_result.scalar() or 0

    rows_result = await db.execute(
        text(f"""
            SELECT al.action, al.resource_type, al.resource_id::text,
                   al.created_at, al.ip_address::text,
                   t.slug AS tenant_slug,
                   u.email AS user_email
            FROM audit_logs al
            LEFT JOIN tenants t ON t.id = al.tenant_id
            LEFT JOIN users u   ON u.id = al.user_id
            {where}
            ORDER BY al.created_at DESC
            LIMIT :limit OFFSET :offset
        """),
        params,
    )

    return {
        "items": [
            {
                "action":       r[0],
                "resource_type": r[1],
                "resource_id":  r[2],
                "created_at":   r[3].isoformat() if r[3] else None,
                "ip":           r[4],
                "tenant":       r[5],
                "user_email":   r[6],
            }
            for r in rows_result.fetchall()
        ],
        "total": int(total),
        "page": page,
        "per_page": per_page,
    }
