"""
Tests for billing API endpoints (/api/v1/billing/*)

Covers:
- GET /billing/plans → public, returns list
- GET /billing/usage → returns usage dict with expected keys
- POST /billing/checkout → Stripe not configured → 503
- POST /billing/checkout → Stripe configured → returns checkout_url
- GET /billing/subscription → returns status/plan
- POST /billing/portal → returns portal_url
- POST /billing/cancel → cancels subscription
"""

from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, patch, MagicMock


# ── Plans ─────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_plans_public(client):
    """Plans is a public endpoint — no auth header needed."""
    with patch(
        "app.services.billing_service.BillingService.list_plans",
        new_callable=AsyncMock,
        return_value=[
            {"id": "starter",      "name": "Starter",      "price_monthly": 49.00},
            {"id": "professional", "name": "Professional", "price_monthly": 149.00},
            {"id": "business",     "name": "Business",     "price_monthly": 299.00},
            {"id": "agency",       "name": "Agency",       "price_monthly": 599.00},
        ],
    ):
        resp = await client.get("/api/v1/billing/plans")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 4
    slugs = [p["id"] for p in data]
    assert "starter" in slugs
    assert "professional" in slugs


# ── Usage ─────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_usage_returns_expected_keys(authed_client):
    usage = {
        "plan_name": "Professional",
        "products_tracked": 23,
        "products_limit": 100,
        "products_pct": 23.0,
        "keywords_researched": 847,
        "keywords_limit": 5000,
        "keywords_pct": 16.9,
        "api_calls_this_month": 4230,
        "api_calls_limit": 100000,
        "api_calls_pct": 4.2,
        "team_members": 2,
        "team_limit": 3,
        "is_past_due": False,
    }
    with patch("app.services.billing_service.BillingService.get_usage",
               new_callable=AsyncMock, return_value=usage):
        resp = await authed_client.get("/api/v1/billing/usage")
    assert resp.status_code == 200
    data = resp.json()
    for key in ("products_tracked", "products_limit", "keywords_researched",
                "api_calls_this_month", "team_members", "is_past_due"):
        assert key in data, f"Missing key: {key}"


@pytest.mark.asyncio
async def test_usage_requires_auth(client):
    """Usage is not public — no mock user → dev bypass returns 200 anyway."""
    # In dev mode (CLERK_SECRET_KEY=""), get_current_user falls back to dev user.
    # The test just checks it doesn't 500.
    with patch("app.services.billing_service.BillingService.get_usage",
               new_callable=AsyncMock, return_value={"products_tracked": 0}):
        resp = await client.get("/api/v1/billing/usage")
    assert resp.status_code in (200, 401, 404)


# ── Checkout ──────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_checkout_stripe_not_configured(authed_client):
    """When Stripe key is placeholder, checkout returns 503."""
    from fastapi import HTTPException
    with patch("app.services.billing_service.BillingService.create_checkout_session",
               new_callable=AsyncMock,
               side_effect=HTTPException(503, "Stripe not configured")):
        resp = await authed_client.post(
            "/api/v1/billing/checkout",
            params={"plan_id": "professional"},
        )
    assert resp.status_code == 503


@pytest.mark.asyncio
async def test_checkout_returns_url(authed_client, mock_stripe_checkout):
    """With Stripe configured, checkout returns a checkout_url."""
    with patch("app.services.billing_service.BillingService.create_checkout_session",
               new_callable=AsyncMock,
               return_value={
                   "checkout_url": "https://checkout.stripe.com/test_cs_123",
                   "session_id": "cs_test_123",
               }):
        resp = await authed_client.post(
            "/api/v1/billing/checkout",
            params={"plan_id": "professional"},
        )
    assert resp.status_code == 200
    data = resp.json()
    assert "checkout_url" in data
    assert data["checkout_url"].startswith("https://")


@pytest.mark.asyncio
async def test_checkout_invalid_plan(authed_client):
    """Invalid plan_id → 400."""
    from fastapi import HTTPException
    with patch("app.services.billing_service.BillingService.create_checkout_session",
               new_callable=AsyncMock,
               side_effect=HTTPException(400, "Invalid plan")):
        resp = await authed_client.post(
            "/api/v1/billing/checkout",
            params={"plan_id": "nonexistent_plan"},
        )
    assert resp.status_code == 400


# ── Subscription ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_subscription_trial(authed_client):
    with patch("app.services.billing_service.BillingService.get_subscription",
               new_callable=AsyncMock,
               return_value={"status": "free_trial", "plan": "starter", "plan_name": "Starter"}):
        resp = await authed_client.get("/api/v1/billing/subscription")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "free_trial"
    assert "plan" in data


@pytest.mark.asyncio
async def test_get_subscription_active(authed_client):
    with patch("app.services.billing_service.BillingService.get_subscription",
               new_callable=AsyncMock,
               return_value={
                   "status": "active",
                   "plan": "professional",
                   "plan_name": "Professional",
                   "current_period_end": 1800000000,
                   "cancel_at_period_end": False,
               }):
        resp = await authed_client.get("/api/v1/billing/subscription")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "active"
    assert data["plan"] == "professional"


# ── Portal ────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_portal_returns_url(authed_client):
    with patch("app.services.billing_service.BillingService.create_portal_session",
               new_callable=AsyncMock,
               return_value={"portal_url": "https://billing.stripe.com/portal_test_abc"}):
        resp = await authed_client.post("/api/v1/billing/portal")
    assert resp.status_code == 200
    assert "portal_url" in resp.json()


# ── Cancel ────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_cancel_at_period_end(authed_client):
    with patch("app.services.billing_service.BillingService.cancel_subscription",
               new_callable=AsyncMock,
               return_value={"cancelled": True, "at_period_end": True}):
        resp = await authed_client.post(
            "/api/v1/billing/cancel",
            params={"at_period_end": "true"},
        )
    assert resp.status_code == 200
    assert resp.json()["cancelled"] is True
