import stripe
import logging
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, text
from app.core.config import settings

stripe.api_key = settings.STRIPE_SECRET_KEY
logger = logging.getLogger(__name__)


def _stripe_configured() -> bool:
    """Return True only when a real Stripe key is present (not empty or the template placeholder)."""
    key = settings.STRIPE_SECRET_KEY or ""
    return bool(key) and key not in ("sk_test_...", "sk_live_...") and len(key) > 20

PLAN_FEATURES = {
    "starter":      {"products": 50,     "keywords": 500,   "api_calls": 10000,  "users": 1,  "marketplaces": 2, "agents": 2, "price": 49},
    "professional": {"products": 100,    "keywords": 5000,  "api_calls": 100000, "users": 3,  "marketplaces": 4, "agents": 5, "price": 149},
    "business":     {"products": 500,    "keywords": 25000, "api_calls": 500000, "users": 10, "marketplaces": 6, "agents": 7, "price": 299},
    "agency":       {"products": -1,     "keywords": -1,    "api_calls": -1,     "users": 25, "marketplaces": 6, "agents": 7, "price": 599},
    "enterprise":   {"products": -1,     "keywords": -1,    "api_calls": -1,     "users": -1, "marketplaces": 6, "agents": 7, "price": 0},
}


class BillingService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Plans ─────────────────────────────────────────────────────
    async def list_plans(self) -> list:
        from app.models.tenant import Plan
        result = await self.db.execute(select(Plan).where(Plan.is_active == True))
        db_plans = result.scalars().all()
        if db_plans:
            return [
                {
                    "id": str(p.id),
                    "name": p.name,
                    "slug": p.name.lower(),
                    "price_monthly": float(p.price_monthly or 0),
                    "price_annual": float(p.price_annual or 0),
                    "limits": p.limits or {},
                    "features": p.features or {},
                    "stripe_price_id": p.stripe_price_id,
                    "is_active": p.is_active,
                }
                for p in db_plans
            ]
        # Fallback: static plan list (no Stripe yet)
        return [
            {
                "id": k,
                "slug": k,
                "name": k.title(),
                "price_monthly": v["price"],
                "limits": {kk: vv for kk, vv in v.items() if kk != "price"},
                "features": _get_plan_features(k),
            }
            for k, v in PLAN_FEATURES.items()
        ]

    # ── Usage (real DB counts) ────────────────────────────────────
    async def get_usage(self, tenant_id: str) -> dict:
        from app.models.tenant import Tenant, Plan
        from app.models.product import Product
        from app.models.keyword import Keyword

        # Load tenant + plan limits
        result = await self.db.execute(
            select(Tenant, Plan)
            .join(Plan, Tenant.plan_id == Plan.id, isouter=True)
            .where(Tenant.id == tenant_id)
        )
        row = result.first()
        tenant = row[0] if row else None
        plan = row[1] if row else None

        # Determine limits from DB plan, fallback to PLAN_FEATURES["professional"]
        if plan and plan.limits:
            limits = plan.limits
            plan_name = plan.name
        else:
            limits = PLAN_FEATURES["professional"]
            plan_name = "Professional"

        # Count tracked products
        products_result = await self.db.execute(
            select(func.count(Product.id)).where(Product.is_tracked == True)
        )
        products_tracked = products_result.scalar() or 0

        # Count keywords researched
        keywords_result = await self.db.execute(
            select(func.count(Keyword.id))
        )
        keywords_count = keywords_result.scalar() or 0

        # Count API calls this month via audit_logs
        month_start = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        api_calls_result = await self.db.execute(
            text("""
                SELECT COUNT(*) FROM audit_logs
                WHERE tenant_id = :tid AND created_at >= :start
            """),
            {"tid": str(tenant_id), "start": month_start},
        )
        api_calls = api_calls_result.scalar() or 0

        # Count AI agent runs today (agent_runs has no tenant_id — count all)
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        ai_calls_result = await self.db.execute(
            text("SELECT COUNT(*) FROM agent_runs WHERE started_at >= :start"),
            {"start": today_start},
        )
        ai_calls = ai_calls_result.scalar() or 0

        # Count team members for this tenant
        team_result = await self.db.execute(
            text("SELECT COUNT(*) FROM tenant_members WHERE tenant_id = :tid"),
            {"tid": str(tenant_id)},
        )
        team_members = team_result.scalar() or 1

        products_limit = int(limits.get("products", 100))
        keywords_limit = int(limits.get("keywords", 5000))
        api_limit = int(limits.get("api_calls", 100000))
        users_limit = int(limits.get("users", 3))

        # Is tenant subscription currently past-due / inactive?
        is_past_due = bool(tenant and not tenant.is_active)

        return {
            "plan_name": plan_name,
            "products_tracked": products_tracked,
            "products_limit": products_limit,
            "products_pct": round((products_tracked / products_limit * 100), 1) if products_limit > 0 else 0,
            # both names for frontend compatibility
            "keywords_researched": keywords_count,
            "keywords_tracked": keywords_count,
            "keywords_limit": keywords_limit,
            "keywords_pct": round((keywords_count / keywords_limit * 100), 1) if keywords_limit > 0 else 0,
            "api_calls_this_month": api_calls,
            "api_calls_limit": api_limit,
            "api_calls_pct": round((api_calls / api_limit * 100), 1) if api_limit > 0 else 0,
            "ai_calls_today": ai_calls,
            "team_members": team_members,
            "team_limit": users_limit,
            "team_pct": round((team_members / users_limit * 100), 1) if users_limit > 0 else 0,
            "is_past_due": is_past_due,
            "limits": limits,
        }

    # ── Stripe Checkout ───────────────────────────────────────────
    async def create_checkout_session(self, tenant_id: str, plan_id: str) -> dict:
        if not _stripe_configured():
            from fastapi import HTTPException
            raise HTTPException(503, "Stripe not configured — add STRIPE_SECRET_KEY to .env")

        plan = PLAN_FEATURES.get(plan_id)
        if not plan:
            from fastapi import HTTPException
            raise HTTPException(400, "Invalid plan")

        from app.models.tenant import Tenant
        result = await self.db.execute(select(Tenant).where(Tenant.id == tenant_id))
        tenant = result.scalar_one_or_none()

        # Get or create Stripe customer
        customer_id = tenant.stripe_customer_id if tenant else None
        if not customer_id:
            customer = stripe.Customer.create(metadata={"tenant_id": str(tenant_id)})
            customer_id = customer.id
            if tenant:
                await self.db.execute(
                    update(Tenant)
                    .where(Tenant.id == tenant_id)
                    .values(stripe_customer_id=customer_id)
                )
                await self.db.commit()

        price_id = _get_stripe_price_id(plan_id)
        if not price_id:
            from fastapi import HTTPException
            raise HTTPException(503, f"Stripe price ID for '{plan_id}' not configured — set STRIPE_{plan_id.upper()}_PRICE_ID in .env")

        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            mode="subscription",
            success_url=f"{settings.FRONTEND_URL}/settings/billing?success=1",
            cancel_url=f"{settings.FRONTEND_URL}/settings/billing?cancelled=1",
            allow_promotion_codes=True,
            trial_period_days=14,
            metadata={"tenant_id": str(tenant_id), "plan_id": plan_id},
        )
        return {"checkout_url": session.url, "session_id": session.id}

    # ── Stripe Portal ─────────────────────────────────────────────
    async def create_portal_session(self, tenant_id: str) -> dict:
        if not _stripe_configured():
            from fastapi import HTTPException
            raise HTTPException(503, "Stripe not configured")

        from app.models.tenant import Tenant
        result = await self.db.execute(select(Tenant).where(Tenant.id == tenant_id))
        tenant = result.scalar_one_or_none()
        if not tenant or not tenant.stripe_customer_id:
            from fastapi import HTTPException
            raise HTTPException(400, "No Stripe customer found — complete a checkout first")

        session = stripe.billing_portal.Session.create(
            customer=tenant.stripe_customer_id,
            return_url=f"{settings.FRONTEND_URL}/settings?section=billing",
        )
        return {"portal_url": session.url}

    # ── Subscription status ───────────────────────────────────────
    async def get_subscription(self, tenant_id: str) -> dict:
        from app.models.tenant import Tenant, Plan
        result = await self.db.execute(
            select(Tenant, Plan)
            .join(Plan, Tenant.plan_id == Plan.id, isouter=True)
            .where(Tenant.id == tenant_id)
        )
        row = result.first()
        tenant = row[0] if row else None
        plan = row[1] if row else None

        if not tenant:
            return {"status": "free_trial", "plan": "starter", "plan_name": "Starter"}

        if not tenant.stripe_subscription_id:
            plan_name = plan.name if plan else "Professional"
            return {
                "status": "free_trial",
                "plan": plan_name.lower(),
                "plan_name": plan_name,
                "trial_ends_at": tenant.trial_ends_at.isoformat() if tenant.trial_ends_at else None,
            }

        if not _stripe_configured():
            return {"status": "active", "plan": "professional", "plan_name": "Professional"}

        try:
            sub = stripe.Subscription.retrieve(tenant.stripe_subscription_id)
            plan_name = plan.name if plan else "Professional"
            return {
                "status": sub.status,
                "plan": plan_name.lower(),
                "plan_name": plan_name,
                "current_period_end": sub.current_period_end,
                "cancel_at_period_end": sub.cancel_at_period_end,
            }
        except stripe.error.StripeError as e:
            logger.warning(f"Stripe subscription fetch failed: {e}")
            plan_name = plan.name if plan else "Professional"
            return {"status": "active", "plan": plan_name.lower(), "plan_name": plan_name}

    async def cancel_subscription(self, tenant_id: str, at_period_end: bool) -> dict:
        from app.models.tenant import Tenant
        result = await self.db.execute(select(Tenant).where(Tenant.id == tenant_id))
        tenant = result.scalar_one_or_none()
        if not tenant or not tenant.stripe_subscription_id:
            from fastapi import HTTPException
            raise HTTPException(400, "No active subscription")
        stripe.Subscription.modify(
            tenant.stripe_subscription_id, cancel_at_period_end=at_period_end
        )
        return {"cancelled": True, "at_period_end": at_period_end}

    # ── Stripe Webhook Handlers ───────────────────────────────────
    async def handle_checkout_completed(self, session: dict) -> None:
        """Activate subscription after successful checkout."""
        tenant_id = session.get("metadata", {}).get("tenant_id")
        plan_id = session.get("metadata", {}).get("plan_id")
        subscription_id = session.get("subscription")

        if not tenant_id:
            logger.warning("checkout.session.completed missing tenant_id in metadata")
            return

        from app.models.tenant import Tenant, Plan
        # Find matching plan by slug
        plan_result = await self.db.execute(
            select(Plan).where(
                func.lower(Plan.name) == (plan_id or "professional").lower()
            )
        )
        plan = plan_result.scalar_one_or_none()

        await self.db.execute(
            update(Tenant)
            .where(Tenant.id == tenant_id)
            .values(
                stripe_subscription_id=subscription_id,
                plan_id=plan.id if plan else None,
                is_active=True,
            )
        )
        await self.db.commit()
        logger.info(f"Tenant {tenant_id} subscribed to plan {plan_id} (sub: {subscription_id})")

    async def handle_subscription_updated(self, subscription: dict) -> None:
        """Sync plan changes (upgrades, downgrades) from Stripe."""
        subscription_id = subscription.get("id")
        status = subscription.get("status")
        # Stripe sends plan info in items[0].price.lookup_key or metadata
        items = subscription.get("items", {}).get("data", [])
        stripe_price_id = items[0]["price"]["id"] if items else None

        from app.models.tenant import Tenant, Plan
        result = await self.db.execute(
            select(Tenant).where(Tenant.stripe_subscription_id == subscription_id)
        )
        tenant = result.scalar_one_or_none()
        if not tenant:
            logger.warning(f"No tenant found for subscription {subscription_id}")
            return

        update_vals: dict = {"is_active": status in ("active", "trialing")}

        # If we can match the price to a plan, update plan_id
        if stripe_price_id:
            plan_result = await self.db.execute(
                select(Plan).where(Plan.stripe_price_id == stripe_price_id)
            )
            plan = plan_result.scalar_one_or_none()
            if plan:
                update_vals["plan_id"] = plan.id

        await self.db.execute(
            update(Tenant).where(Tenant.id == tenant.id).values(**update_vals)
        )
        await self.db.commit()
        logger.info(f"Tenant {tenant.id} subscription updated: status={status}, price={stripe_price_id}")

    async def handle_subscription_deleted(self, subscription: dict) -> None:
        """Downgrade tenant to Starter on subscription cancellation."""
        subscription_id = subscription.get("id")

        from app.models.tenant import Tenant, Plan
        result = await self.db.execute(
            select(Tenant).where(Tenant.stripe_subscription_id == subscription_id)
        )
        tenant = result.scalar_one_or_none()
        if not tenant:
            return

        # Find starter plan
        starter_result = await self.db.execute(
            select(Plan).where(func.lower(Plan.name) == "starter")
        )
        starter = starter_result.scalar_one_or_none()

        await self.db.execute(
            update(Tenant)
            .where(Tenant.id == tenant.id)
            .values(
                stripe_subscription_id=None,
                plan_id=starter.id if starter else None,
                is_active=True,  # Still active on free tier
            )
        )
        await self.db.commit()
        logger.info(f"Tenant {tenant.id} downgraded to Starter (subscription {subscription_id} deleted)")

    async def handle_payment_failed(self, invoice: dict) -> None:
        """Mark tenant past-due on payment failure; log for dunning."""
        customer_id = invoice.get("customer")
        amount = invoice.get("amount_due", 0)
        logger.warning(f"Payment failed for Stripe customer {customer_id}: ${amount/100:.2f}")

        if customer_id:
            from app.models.tenant import Tenant
            result = await self.db.execute(
                select(Tenant).where(Tenant.stripe_customer_id == customer_id)
            )
            tenant = result.scalar_one_or_none()
            if tenant:
                # Grace period: don't hard-lock, but flag as past-due via is_active=False
                # Restore happens in handle_subscription_updated when status becomes 'active'
                await self.db.execute(
                    update(Tenant).where(Tenant.id == tenant.id).values(is_active=False)
                )
                await self.db.commit()
                logger.info(f"Tenant {tenant.id} flagged past-due (payment failed)")


# ── Helpers ───────────────────────────────────────────────────────
def _get_stripe_price_id(plan_id: str) -> str:
    price_map = {
        "starter":      settings.STRIPE_STARTER_PRICE_ID,
        "professional": settings.STRIPE_PROFESSIONAL_PRICE_ID,
        "business":     settings.STRIPE_BUSINESS_PRICE_ID,
        "agency":       settings.STRIPE_AGENCY_PRICE_ID,
    }
    return price_map.get(plan_id, "")


def _get_plan_features(plan_id: str) -> list:
    base = ["Product Research", "Keyword Intelligence", "AI CEO Dashboard"]
    by_plan = {
        "starter":      base,
        "professional": base + ["Launch Simulator", "Saturation Radar", "AI Agents (5)", "Listing Builder"],
        "business":     base + ["All AI Agents", "Digital Twin", "Voice Assistant", "All Marketplaces", "Automation"],
        "agency":       base + ["Everything in Business", "White Label", "25 Users", "Agency Dashboard"],
        "enterprise":   ["Everything + Custom AI Models", "Dedicated Infrastructure", "SLA"],
    }
    return by_plan.get(plan_id, base)
