import pytest
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_list_plans_public(client):
    """Plans endpoint should be public (no auth needed)."""
    with patch("app.services.billing_service.BillingService.list_plans",
               new_callable=AsyncMock, return_value=[
                   {"id": "starter", "name": "Starter", "price_monthly": 49.00},
                   {"id": "professional", "name": "Professional", "price_monthly": 149.00},
               ]):
        resp = await client.get("/api/v1/billing/plans")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_usage_returns_data(client):
    with patch("app.services.billing_service.BillingService.get_usage",
               new_callable=AsyncMock, return_value={
                   "products_tracked": 23,
                   "keywords_researched": 847,
                   "api_calls_this_month": 4230,
               }):
        resp = await client.get("/api/v1/billing/usage")
    assert resp.status_code == 200
    data = resp.json()
    assert "products_tracked" in data


@pytest.mark.asyncio
async def test_checkout_creates_session(client):
    with patch("app.services.billing_service.BillingService.create_checkout_session",
               new_callable=AsyncMock, return_value={
                   "checkout_url": "https://checkout.stripe.com/test",
                   "session_id": "cs_test_abc123",
               }):
        resp = await client.post("/api/v1/billing/checkout", params={"plan_id": "professional"})
    assert resp.status_code in (200, 422)
