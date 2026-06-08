"""
Tests for Stripe + Clerk webhook handlers (/api/v1/webhooks/*)

Covers:
- Stripe webhook: missing/invalid signature → 400
- checkout.session.completed → tenant activated + plan set
- customer.subscription.updated → is_active reflects status
- customer.subscription.deleted → tenant downgraded to Starter
- invoice.paid → past-due tenant re-activated
- invoice.payment_failed → tenant flagged past-due
- Clerk webhook: user.created → user provisioned
- Unhandled Stripe events → 200 (ignored gracefully)
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient


def _stripe_event(event_type: str, data: dict) -> dict:
    """Build a minimal Stripe event payload."""
    return {
        "id": f"evt_{uuid.uuid4().hex[:20]}",
        "type": event_type,
        "data": {"object": data},
        "api_version": "2024-06-20",
    }


def _post_webhook(client: AsyncClient, payload: dict, sig: str = "t=1,v1=fake"):
    return client.post(
        "/api/v1/webhooks/stripe",
        content=json.dumps(payload).encode(),
        headers={"stripe-signature": sig, "Content-Type": "application/json"},
    )


# ── Signature verification ────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_stripe_webhook_invalid_signature(client: AsyncClient):
    """Invalid Stripe signature → 400."""
    import stripe
    with patch.object(
        stripe.Webhook,
        "construct_event",
        side_effect=stripe.error.SignatureVerificationError("bad sig", "bad sig"),
    ):
        resp = await _post_webhook(client, _stripe_event("checkout.session.completed", {}))
    assert resp.status_code == 400


# ── checkout.session.completed ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_checkout_completed_activates_tenant(client: AsyncClient):
    """checkout.session.completed → handle_checkout_completed called."""
    tenant_id = str(uuid.uuid4())
    event = _stripe_event("checkout.session.completed", {
        "metadata": {"tenant_id": tenant_id, "plan_id": "professional"},
        "subscription": "sub_test_123",
        "amount_total": 14900,
    })
    with patch("stripe.Webhook.construct_event", return_value=event), \
         patch("app.services.billing_service.BillingService.handle_checkout_completed",
               new_callable=AsyncMock) as mock_handler:
        resp = await _post_webhook(client, event, sig="t=123,v1=valid")
    assert resp.status_code == 200
    assert resp.json() == {"received": True}
    mock_handler.assert_awaited_once()


# ── customer.subscription.updated ────────────────────────────────────────────

@pytest.mark.asyncio
async def test_subscription_updated_calls_handler(client: AsyncClient):
    event = _stripe_event("customer.subscription.updated", {
        "id": "sub_test_abc",
        "status": "active",
        "items": {"data": [{"price": {"id": "price_prof_monthly"}}]},
    })
    with patch("stripe.Webhook.construct_event", return_value=event), \
         patch("app.services.billing_service.BillingService.handle_subscription_updated",
               new_callable=AsyncMock) as mock_handler:
        resp = await _post_webhook(client, event)
    assert resp.status_code == 200
    mock_handler.assert_awaited_once()


@pytest.mark.asyncio
async def test_subscription_updated_past_due(client: AsyncClient):
    """past_due status should be forwarded to the handler."""
    event = _stripe_event("customer.subscription.updated", {
        "id": "sub_test_abc",
        "status": "past_due",
        "items": {"data": []},
    })
    with patch("stripe.Webhook.construct_event", return_value=event), \
         patch("app.services.billing_service.BillingService.handle_subscription_updated",
               new_callable=AsyncMock) as mock_handler:
        resp = await _post_webhook(client, event)
    assert resp.status_code == 200
    # Verify the handler received the past_due status
    call_arg = mock_handler.call_args[0][0]
    assert call_arg["status"] == "past_due"


# ── customer.subscription.deleted ────────────────────────────────────────────

@pytest.mark.asyncio
async def test_subscription_deleted_calls_handler(client: AsyncClient):
    event = _stripe_event("customer.subscription.deleted", {
        "id": "sub_test_abc",
        "current_period_end": 1800000000,
    })
    with patch("stripe.Webhook.construct_event", return_value=event), \
         patch("app.services.billing_service.BillingService.handle_subscription_deleted",
               new_callable=AsyncMock) as mock_handler:
        resp = await _post_webhook(client, event)
    assert resp.status_code == 200
    mock_handler.assert_awaited_once()


# ── invoice.paid ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_invoice_paid_reactivates_tenant(client: AsyncClient):
    """invoice.paid → handle_invoice_paid called."""
    event = _stripe_event("invoice.paid", {
        "customer": "cus_test_abc",
        "amount_paid": 14900,
        "status": "paid",
    })
    with patch("stripe.Webhook.construct_event", return_value=event), \
         patch("app.services.billing_service.BillingService.handle_invoice_paid",
               new_callable=AsyncMock) as mock_handler:
        resp = await _post_webhook(client, event)
    assert resp.status_code == 200
    mock_handler.assert_awaited_once()


# ── invoice.payment_failed ────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_payment_failed_flags_tenant(client: AsyncClient):
    event = _stripe_event("invoice.payment_failed", {
        "customer": "cus_test_abc",
        "amount_due": 14900,
    })
    with patch("stripe.Webhook.construct_event", return_value=event), \
         patch("app.services.billing_service.BillingService.handle_payment_failed",
               new_callable=AsyncMock) as mock_handler:
        resp = await _post_webhook(client, event)
    assert resp.status_code == 200
    mock_handler.assert_awaited_once()


# ── Unhandled event types ─────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_unhandled_stripe_event_returns_200(client: AsyncClient):
    """Unknown event types should be silently ignored (no 4xx/5xx)."""
    event = _stripe_event("payment_intent.created", {"id": "pi_test"})
    with patch("stripe.Webhook.construct_event", return_value=event):
        resp = await _post_webhook(client, event)
    assert resp.status_code == 200
    assert resp.json() == {"received": True}


# ── Clerk webhook ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_clerk_user_created_event(client: AsyncClient):
    """Clerk user.created → UserService.sync_clerk_user called."""
    clerk_payload = {
        "type": "user.created",
        "data": {
            "id": "user_clerk_abc123",
            "email_addresses": [{"email_address": "newuser@test.com"}],
            "first_name": "New",
            "last_name": "User",
        },
    }
    with patch("app.services.user_service.UserService.sync_clerk_user",
               new_callable=AsyncMock) as mock_sync:
        resp = await client.post(
            "/api/v1/webhooks/clerk",
            json=clerk_payload,
        )
    assert resp.status_code == 200
    mock_sync.assert_awaited_once()


@pytest.mark.asyncio
async def test_clerk_user_deleted_event(client: AsyncClient):
    clerk_payload = {
        "type": "user.deleted",
        "data": {"id": "user_clerk_abc123"},
    }
    with patch("app.services.user_service.UserService.deactivate_user",
               new_callable=AsyncMock) as mock_deactivate:
        resp = await client.post(
            "/api/v1/webhooks/clerk",
            json=clerk_payload,
        )
    assert resp.status_code == 200
    mock_deactivate.assert_awaited_once_with("user_clerk_abc123")


# ── BillingService unit: handle_invoice_paid ─────────────────────────────────

@pytest.mark.asyncio
async def test_handle_invoice_paid_restores_active(db_session):
    """Unit test: handle_invoice_paid sets is_active=True for past-due tenant."""
    import uuid as _uuid
    from sqlalchemy import update, select
    from app.models.tenant import Tenant, Plan
    from app.services.billing_service import BillingService
    from decimal import Decimal

    cus_id = "cus_test_invoice_paid"
    plan = Plan(
        id=_uuid.uuid4(), name="Professional", price_monthly=Decimal("149.00"),
        limits={}, features={}, is_active=True,
    )
    db_session.add(plan)
    tenant = Tenant(
        id=_uuid.uuid4(), slug="invoice-paid-tenant",
        name="Invoice Paid Corp", plan_id=plan.id,
        stripe_customer_id=cus_id, is_active=False,  # past-due
    )
    db_session.add(tenant)
    await db_session.commit()

    service = BillingService(db_session)
    await service.handle_invoice_paid({"customer": cus_id})

    result = await db_session.execute(
        select(Tenant.is_active).where(Tenant.id == tenant.id)
    )
    assert result.scalar() is True


@pytest.mark.asyncio
async def test_handle_invoice_paid_no_op_for_unknown_customer(db_session):
    """handle_invoice_paid with unknown customer_id → no error."""
    from app.services.billing_service import BillingService
    service = BillingService(db_session)
    # Should not raise
    await service.handle_invoice_paid({"customer": "cus_does_not_exist"})


@pytest.mark.asyncio
async def test_handle_subscription_deleted_downgrades_to_starter(db_session):
    """handle_subscription_deleted clears stripe_subscription_id."""
    import uuid as _uuid
    from sqlalchemy import select
    from app.models.tenant import Tenant, Plan
    from app.services.billing_service import BillingService
    from decimal import Decimal

    sub_id = "sub_to_be_deleted"
    starter = Plan(
        id=_uuid.uuid4(), name="Starter", price_monthly=Decimal("49.00"),
        limits={}, features={}, is_active=True,
    )
    pro = Plan(
        id=_uuid.uuid4(), name="Professional", price_monthly=Decimal("149.00"),
        limits={}, features={}, is_active=True,
    )
    db_session.add_all([starter, pro])
    tenant = Tenant(
        id=_uuid.uuid4(), slug="cancel-tenant",
        name="Cancel Corp", plan_id=pro.id,
        stripe_subscription_id=sub_id, is_active=True,
    )
    db_session.add(tenant)
    await db_session.commit()

    service = BillingService(db_session)
    await service.handle_subscription_deleted({
        "id": sub_id,
        "current_period_end": 1800000000,
    })

    result = await db_session.execute(
        select(Tenant.stripe_subscription_id, Tenant.plan_id)
        .where(Tenant.id == tenant.id)
    )
    row = result.first()
    assert row.stripe_subscription_id is None
    assert row.plan_id == starter.id
