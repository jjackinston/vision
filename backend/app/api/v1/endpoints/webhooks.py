from fastapi import APIRouter, Request, HTTPException, Header
from typing import Optional
import stripe
import json
import logging

from app.core.config import settings
from app.services.billing_service import BillingService
from app.core.database import AsyncSessionLocal

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: Optional[str] = Header(None, alias="stripe-signature"),
):
    payload = await request.body()
    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError) as e:
        raise HTTPException(status_code=400, detail=str(e))

    async with AsyncSessionLocal() as db:
        service = BillingService(db)
        etype = event["type"]

        if etype == "checkout.session.completed":
            await service.handle_checkout_completed(event["data"]["object"])
        elif etype == "customer.subscription.updated":
            await service.handle_subscription_updated(event["data"]["object"])
        elif etype == "customer.subscription.deleted":
            await service.handle_subscription_deleted(event["data"]["object"])
        elif etype == "invoice.paid":
            # Re-activate tenants that were flagged past-due after payment succeeds
            await service.handle_invoice_paid(event["data"]["object"])
        elif etype == "invoice.payment_failed":
            await service.handle_payment_failed(event["data"]["object"])
        else:
            logger.info(f"Unhandled Stripe event: {etype}")

    return {"received": True}


@router.post("/clerk")
async def clerk_webhook(request: Request):
    """Handle Clerk user lifecycle events (user.created / updated / deleted)."""
    payload_bytes = await request.body()

    # Verify svix signature when CLERK_WEBHOOK_SECRET is configured
    if settings.CLERK_WEBHOOK_SECRET:
        try:
            from svix.webhooks import Webhook, WebhookVerificationError
            wh = Webhook(settings.CLERK_WEBHOOK_SECRET)
            wh.verify(
                payload_bytes,
                {
                    "svix-id": request.headers.get("svix-id", ""),
                    "svix-timestamp": request.headers.get("svix-timestamp", ""),
                    "svix-signature": request.headers.get("svix-signature", ""),
                },
            )
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Webhook signature invalid: {exc}")

    payload = json.loads(payload_bytes)
    event_type = payload.get("type")

    async with AsyncSessionLocal() as db:
        from app.services.user_service import UserService
        service = UserService(db)

        if event_type == "user.created":
            await service.sync_clerk_user(payload["data"])
        elif event_type == "user.updated":
            await service.update_clerk_user(payload["data"])
        elif event_type == "user.deleted":
            await service.deactivate_user(payload["data"]["id"])
        else:
            logger.info(f"Unhandled Clerk event: {event_type}")

    return {"received": True}


@router.post("/amazon")
async def amazon_webhook(request: Request):
    """Handle Amazon SP-API notifications (orders, inventory alerts)."""
    payload = await request.json()
    notification_type = payload.get("notificationType")
    logger.info(f"Amazon notification: {notification_type}")

    if notification_type == "ORDER_CHANGE":
        from app.workers.tasks import sync_all_inventory
        sync_all_inventory.delay()
    elif notification_type == "ITEM_INVENTORY_EVENT_CHANGE":
        from app.workers.tasks import update_all_product_metrics
        update_all_product_metrics.delay()

    return {"received": True}
