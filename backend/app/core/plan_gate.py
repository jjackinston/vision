"""
Plan-gate utilities for SellerVision AI.

Usage
-----
# Gate an entire endpoint to a minimum plan tier:
    from app.core.plan_gate import require_plan

    @router.post("/agents/{agent_id}/run")
    async def run_agent(
        agent_id: str,
        user: CurrentUser = Depends(require_plan("professional")),
    ):
        ...

# Enforce a resource count limit before a write operation:
    from app.core.plan_gate import enforce_limit

    await enforce_limit(db, user.tenant_id, "products", current_tracked_count)

Plan tiers (lower number = lower tier):
    starter=0  professional=1  business=2  agency=3  enterprise=4
"""

from __future__ import annotations

import logging
from typing import Optional

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.core.security import security, get_current_user, CurrentUser

logger = logging.getLogger(__name__)

# ── Plan ordering ─────────────────────────────────────────────────────────────

PLAN_TIERS: dict[str, int] = {
    "starter":      0,
    "professional": 1,
    "business":     2,
    "agency":       3,
    "enterprise":   4,
}

# Human-readable upgrade target messaging
_PLAN_DISPLAY: dict[str, str] = {
    "starter":      "Starter ($49/mo)",
    "professional": "Professional ($149/mo)",
    "business":     "Business ($299/mo)",
    "agency":       "Agency ($599/mo)",
    "enterprise":   "Enterprise",
}

# How many days a trial gets before auto-expiry
TRIAL_DAYS = 14


# ── Tenant plan lookup (thin wrapper — no Redis here to keep it simple) ───────

async def _get_tenant_plan_name(db: AsyncSession, tenant_id: str) -> str:
    """Return the lowercase plan name for a tenant, defaulting to 'starter'."""
    from app.models.tenant import Tenant, Plan

    result = await db.execute(
        select(Plan.name)
        .join(Tenant, Tenant.plan_id == Plan.id)
        .where(Tenant.id == tenant_id)
    )
    name = result.scalar_one_or_none()
    return (name or "starter").lower()


async def _get_tenant_plan_limits(db: AsyncSession, tenant_id: str) -> dict:
    """Return the JSONB limits dict for the tenant's current plan."""
    from app.models.tenant import Tenant, Plan
    from app.services.billing_service import PLAN_FEATURES

    result = await db.execute(
        select(Plan.limits, Plan.name)
        .join(Tenant, Tenant.plan_id == Plan.id)
        .where(Tenant.id == tenant_id)
    )
    row = result.first()
    if row and row[0]:
        return dict(row[0])
    # Fallback to hard-coded defaults when DB has no plan row
    plan_name = (row[1] if row else "professional").lower()
    return PLAN_FEATURES.get(plan_name, PLAN_FEATURES["professional"])


# ── FastAPI dependency factory ────────────────────────────────────────────────

def require_plan(min_plan: str):
    """
    FastAPI dependency factory.  Resolves the current user *and* verifies that
    the tenant's plan is at or above `min_plan`.  Raises:
      - 401 if not authenticated
      - 402 if trial expired with no active subscription
      - 403 if the plan tier is too low (with upgrade hint in the detail)

    Example
    -------
        @router.post("/run")
        async def run_agent(user: CurrentUser = Depends(require_plan("professional"))):
            ...
    """
    min_tier = PLAN_TIERS.get(min_plan.lower(), 1)

    async def _dep(
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
        db: AsyncSession = Depends(get_db),
    ) -> CurrentUser:
        # Reuse the standard auth path
        user = await get_current_user(credentials, db)

        # Check tenant subscription status + trial expiry
        await _assert_subscription_active(db, user.tenant_id)

        # Check plan tier
        plan_name = await _get_tenant_plan_name(db, user.tenant_id)
        tenant_tier = PLAN_TIERS.get(plan_name, 0)

        if tenant_tier < min_tier:
            required_display = _PLAN_DISPLAY.get(min_plan.lower(), min_plan.title())
            raise HTTPException(
                status_code=403,
                detail={
                    "code": "PLAN_UPGRADE_REQUIRED",
                    "message": f"This feature requires the {required_display} plan or higher.",
                    "current_plan": plan_name,
                    "required_plan": min_plan.lower(),
                    "upgrade_url": "/settings?section=billing",
                },
            )

        return user

    return _dep


# ── Subscription + trial expiry assertion (shared) ───────────────────────────

async def _assert_subscription_active(db: AsyncSession, tenant_id: str) -> None:
    """
    Raises HTTP 402 if:
      - Tenant.is_active is False  (payment past-due), OR
      - Trial has expired AND there is no Stripe subscription
    """
    from app.models.tenant import Tenant
    from datetime import datetime, timezone

    result = await db.execute(
        select(Tenant.is_active, Tenant.trial_ends_at, Tenant.stripe_subscription_id)
        .where(Tenant.id == tenant_id)
    )
    row = result.first()
    if row is None:
        return  # Dev / unknown tenant — pass through

    is_active, trial_ends_at, stripe_sub_id = row

    # Past-due payment flag
    if is_active is False:
        raise HTTPException(
            status_code=402,
            detail={
                "code": "PAYMENT_PAST_DUE",
                "message": "Your payment is past-due. Please update your payment method.",
                "upgrade_url": "/settings?section=billing",
            },
        )

    # Trial expiry check (only enforced when there is no paid subscription)
    if not stripe_sub_id and trial_ends_at:
        now = datetime.now(timezone.utc)
        if trial_ends_at.replace(tzinfo=timezone.utc) < now:
            raise HTTPException(
                status_code=402,
                detail={
                    "code": "TRIAL_EXPIRED",
                    "message": "Your free trial has expired. Upgrade to continue.",
                    "upgrade_url": "/settings?section=billing",
                },
            )


# ── Resource limit enforcement ────────────────────────────────────────────────

async def enforce_limit(
    db: AsyncSession,
    tenant_id: str,
    resource: str,
    current_count: int,
) -> None:
    """
    Compare `current_count` against the tenant plan's limit for `resource`.
    Raises HTTP 402 if the limit is reached.

    `resource` should match a key in PLAN_FEATURES / plan.limits:
        "products", "keywords", "users", "api_calls", "agents"

    Pass -1 limits as unlimited (Agency / Enterprise).

    Example
    -------
        tracked = await db.scalar(select(func.count(Product.id)).where(...))
        await enforce_limit(db, user.tenant_id, "products", tracked)
    """
    limits = await _get_tenant_plan_limits(db, tenant_id)
    limit = int(limits.get(resource, -1))

    if limit == -1:
        return  # Unlimited (Agency/Enterprise)

    if current_count >= limit:
        from app.models.tenant import Tenant, Plan

        plan_result = await db.execute(
            select(Plan.name)
            .join(Tenant, Tenant.plan_id == Plan.id)
            .where(Tenant.id == tenant_id)
        )
        plan_name = (plan_result.scalar_one_or_none() or "Starter").lower()

        # Suggest the next tier up
        current_tier = PLAN_TIERS.get(plan_name, 0)
        next_plan = next(
            (name for name, tier in sorted(PLAN_TIERS.items(), key=lambda x: x[1]) if tier > current_tier),
            "agency",
        )
        next_display = _PLAN_DISPLAY.get(next_plan, next_plan.title())

        raise HTTPException(
            status_code=402,
            detail={
                "code": "LIMIT_REACHED",
                "message": (
                    f"You've reached your plan's {resource} limit ({limit}). "
                    f"Upgrade to {next_display} to add more."
                ),
                "resource": resource,
                "limit": limit,
                "current": current_count,
                "upgrade_url": "/settings?section=billing",
            },
        )
