from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import stripe
from app.core.database import get_db
from app.core.security import get_current_user, CurrentUser
from app.core.config import settings
from app.services.billing_service import BillingService

router = APIRouter()
stripe.api_key = settings.STRIPE_SECRET_KEY


@router.get("/plans")
async def list_plans(db: AsyncSession = Depends(get_db)):
    """Public endpoint — no auth required."""
    service = BillingService(db)
    return await service.list_plans()


@router.get("/usage")
async def get_usage(
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    service = BillingService(db)
    return await service.get_usage(user.tenant_id)


@router.post("/checkout")
async def create_checkout_session(
    plan_id: str,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """Create Stripe Checkout session for plan subscription."""
    user.require("billing")
    service = BillingService(db)
    return await service.create_checkout_session(user.tenant_id, plan_id)


@router.post("/portal")
async def customer_portal(
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """Open Stripe customer portal for billing management."""
    user.require("billing")
    service = BillingService(db)
    return await service.create_portal_session(user.tenant_id)


@router.get("/subscription")
async def get_subscription(
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    service = BillingService(db)
    return await service.get_subscription(user.tenant_id)


@router.post("/cancel")
async def cancel_subscription(
    at_period_end: bool = True,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    user.require("billing")
    service = BillingService(db)
    return await service.cancel_subscription(user.tenant_id, at_period_end)
