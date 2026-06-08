"""
Tests for app/core/plan_gate.py

Covers:
- PLAN_TIERS ordering
- require_plan() raises 403 when plan tier is too low
- require_plan() passes when plan tier is sufficient
- enforce_limit() raises 402 at limit
- enforce_limit() passes when under limit
- enforce_limit() passes for unlimited plans (limit = -1)
- _assert_subscription_active() raises 402 when is_active=False (past-due)
- _assert_subscription_active() raises 402 when trial expired + no subscription
- _assert_subscription_active() passes within active trial
- Digital-Twin endpoint gated to Business plan
- Agent run endpoint gated to Professional plan
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient

from app.core.plan_gate import (
    PLAN_TIERS,
    enforce_limit,
    _assert_subscription_active,
)
from tests.conftest import (
    OWNER_TENANT_ID,
    OWNER_USER_ID,
    TENANT_SLUG,
    make_mock_user,
    seed_tenant,
)


# ── PLAN_TIERS ────────────────────────────────────────────────────────────────

def test_plan_tier_ordering():
    assert PLAN_TIERS["starter"]      < PLAN_TIERS["professional"]
    assert PLAN_TIERS["professional"] < PLAN_TIERS["business"]
    assert PLAN_TIERS["business"]     < PLAN_TIERS["agency"]
    assert PLAN_TIERS["agency"]       < PLAN_TIERS["enterprise"]


def test_plan_tiers_complete():
    for plan in ("starter", "professional", "business", "agency", "enterprise"):
        assert plan in PLAN_TIERS, f"Missing plan: {plan}"


# ── enforce_limit ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_enforce_limit_under_limit(db_session):
    """Under the limit → no exception raised."""
    await seed_tenant(db_session)
    # 10 products tracked, limit is 100 — should pass silently
    await enforce_limit(db_session, OWNER_TENANT_ID, "products", current_count=10)


@pytest.mark.asyncio
async def test_enforce_limit_at_limit_raises(db_session):
    """At the limit → HTTP 402."""
    from fastapi import HTTPException
    await seed_tenant(db_session)
    with pytest.raises(HTTPException) as exc_info:
        await enforce_limit(db_session, OWNER_TENANT_ID, "products", current_count=100)
    assert exc_info.value.status_code == 402
    detail = exc_info.value.detail
    assert detail["code"] == "LIMIT_REACHED"
    assert detail["resource"] == "products"
    assert detail["limit"] == 100
    assert "upgrade_url" in detail


@pytest.mark.asyncio
async def test_enforce_limit_above_limit_raises(db_session):
    """Above the limit also raises (defensive check)."""
    from fastapi import HTTPException
    await seed_tenant(db_session)
    with pytest.raises(HTTPException) as exc_info:
        await enforce_limit(db_session, OWNER_TENANT_ID, "products", current_count=150)
    assert exc_info.value.status_code == 402


@pytest.mark.asyncio
async def test_enforce_limit_unlimited_passes(db_session):
    """limit=-1 (Agency/Enterprise) → always passes, any count."""
    from decimal import Decimal
    from app.models.tenant import Plan, Tenant, TenantMember
    # Create an Agency plan with products=-1
    agency_tenant_id = str(uuid.uuid4())
    plan = Plan(
        id=uuid.uuid4(),
        name="Agency",
        price_monthly=Decimal("599.00"),
        limits={"products": -1, "keywords": -1, "api_calls": -1, "users": 25, "agents": 7},
        features={},
        is_active=True,
    )
    db_session.add(plan)
    tenant = Tenant(
        id=uuid.UUID(agency_tenant_id),
        slug="agency-tenant",
        name="Agency Test",
        plan_id=plan.id,
        is_active=True,
    )
    db_session.add(tenant)
    await db_session.commit()

    # Should not raise even with 99999 products
    await enforce_limit(db_session, agency_tenant_id, "products", current_count=99999)


@pytest.mark.asyncio
async def test_enforce_limit_users(db_session):
    """Users limit enforced: plan has users=3."""
    from fastapi import HTTPException
    await seed_tenant(db_session)
    # 3 members already → over limit
    with pytest.raises(HTTPException) as exc_info:
        await enforce_limit(db_session, OWNER_TENANT_ID, "users", current_count=3)
    assert exc_info.value.status_code == 402
    assert exc_info.value.detail["resource"] == "users"


# ── _assert_subscription_active ───────────────────────────────────────────────

@pytest.mark.asyncio
async def test_assert_active_passes_for_active_tenant(db_session):
    """Active tenant with paid subscription → no exception."""
    await seed_tenant(db_session, stripe_sub_id="sub_abc123", is_active=True)
    await _assert_subscription_active(db_session, OWNER_TENANT_ID)  # no exception


@pytest.mark.asyncio
async def test_assert_active_raises_for_past_due(db_session):
    """is_active=False → 402 PAYMENT_PAST_DUE."""
    from fastapi import HTTPException
    await seed_tenant(db_session, stripe_sub_id="sub_abc123", is_active=False)
    with pytest.raises(HTTPException) as exc_info:
        await _assert_subscription_active(db_session, OWNER_TENANT_ID)
    assert exc_info.value.status_code == 402
    assert exc_info.value.detail["code"] == "PAYMENT_PAST_DUE"


@pytest.mark.asyncio
async def test_assert_active_raises_for_expired_trial(db_session):
    """trial_ends_at in the past + no stripe sub → 402 TRIAL_EXPIRED."""
    from fastapi import HTTPException
    expired = datetime.now(timezone.utc) - timedelta(days=1)
    await seed_tenant(db_session, stripe_sub_id=None, trial_ends_at=expired, is_active=True)
    with pytest.raises(HTTPException) as exc_info:
        await _assert_subscription_active(db_session, OWNER_TENANT_ID)
    assert exc_info.value.status_code == 402
    assert exc_info.value.detail["code"] == "TRIAL_EXPIRED"


@pytest.mark.asyncio
async def test_assert_active_passes_within_trial(db_session):
    """trial_ends_at in the future + no stripe sub → OK."""
    future = datetime.now(timezone.utc) + timedelta(days=7)
    await seed_tenant(db_session, stripe_sub_id=None, trial_ends_at=future, is_active=True)
    await _assert_subscription_active(db_session, OWNER_TENANT_ID)  # no exception


@pytest.mark.asyncio
async def test_assert_active_passes_when_no_trial_date(db_session):
    """No trial_ends_at and no subscription → treated as unlimited trial (no gate)."""
    await seed_tenant(db_session, stripe_sub_id=None, trial_ends_at=None, is_active=True)
    await _assert_subscription_active(db_session, OWNER_TENANT_ID)  # no exception


# ── require_plan via HTTP ──────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_agent_run_requires_professional(authed_client: AsyncClient, db_session):
    """POST /agents/{name}/run is gated to Professional plan.
    Mock require_plan to raise 403 for a starter-only user."""
    from fastapi import HTTPException

    with patch("app.core.plan_gate._get_tenant_plan_name",
               new=AsyncMock(return_value="starter")), \
         patch("app.core.plan_gate._assert_subscription_active",
               new=AsyncMock(return_value=None)):
        resp = await authed_client.post(
            "/api/v1/agents/product_research/run",
            json={"task": "Find top bamboo products", "context": {}}
        )
    # 403 because starter < professional
    assert resp.status_code == 403
    detail = resp.json()["detail"]
    assert detail["code"] == "PLAN_UPGRADE_REQUIRED"
    assert detail["required_plan"] == "professional"


@pytest.mark.asyncio
async def test_agent_run_allowed_for_professional(authed_client: AsyncClient):
    """POST /agents/{name}/run succeeds for Professional plan."""
    with patch("app.core.plan_gate._get_tenant_plan_name",
               new=AsyncMock(return_value="professional")), \
         patch("app.core.plan_gate._assert_subscription_active",
               new=AsyncMock(return_value=None)):
        resp = await authed_client.post(
            "/api/v1/agents/product_research/run",
            json={"task": "Find top products", "context": {}}
        )
    # Endpoint itself may 503 (Celery not running) but NOT 403
    assert resp.status_code != 403


@pytest.mark.asyncio
async def test_simulate_requires_business(authed_client: AsyncClient):
    """POST /analytics/simulate is gated to Business plan."""
    with patch("app.core.plan_gate._get_tenant_plan_name",
               new=AsyncMock(return_value="professional")), \
         patch("app.core.plan_gate._assert_subscription_active",
               new=AsyncMock(return_value=None)):
        resp = await authed_client.post(
            "/api/v1/analytics/simulate",
            params={"scenario_type": "price_change", "forecast_months": 3},
            json={"price_delta_pct": 10},
        )
    assert resp.status_code == 403
    assert resp.json()["detail"]["code"] == "PLAN_UPGRADE_REQUIRED"
    assert resp.json()["detail"]["required_plan"] == "business"


@pytest.mark.asyncio
async def test_simulate_allowed_for_business(authed_client: AsyncClient):
    """POST /analytics/simulate passes plan gate for Business plan."""
    with patch("app.core.plan_gate._get_tenant_plan_name",
               new=AsyncMock(return_value="business")), \
         patch("app.core.plan_gate._assert_subscription_active",
               new=AsyncMock(return_value=None)), \
         patch("app.services.ceo_dashboard_service.DigitalTwinService.simulate",
               new_callable=AsyncMock, return_value={"scenarios": []}):
        resp = await authed_client.post(
            "/api/v1/analytics/simulate",
            params={"scenario_type": "price_change", "forecast_months": 3},
            json={"price_delta_pct": 10},
        )
    assert resp.status_code != 403


# ── Track product limit enforcement via HTTP ──────────────────────────────────

@pytest.mark.asyncio
async def test_track_product_at_limit_returns_402(authed_client: AsyncClient):
    """Tracking a product when at plan limit → 402."""
    fake_id = str(uuid.uuid4())
    with patch("app.core.plan_gate._assert_subscription_active",
               new=AsyncMock(return_value=None)), \
         patch("app.core.plan_gate.enforce_limit",
               new=AsyncMock(side_effect=__import__("fastapi").HTTPException(
                   status_code=402,
                   detail={"code": "LIMIT_REACHED", "resource": "products",
                            "limit": 50, "current": 50, "upgrade_url": "/settings"}
               ))):
        resp = await authed_client.post(f"/api/v1/products/{fake_id}/track")
    assert resp.status_code == 402
    assert resp.json()["detail"]["code"] == "LIMIT_REACHED"


@pytest.mark.asyncio
async def test_track_product_under_limit_proceeds(authed_client: AsyncClient):
    """Tracking under the plan limit → proceeds (404 on unknown product is fine)."""
    fake_id = str(uuid.uuid4())
    with patch("app.core.plan_gate._assert_subscription_active",
               new=AsyncMock(return_value=None)), \
         patch("app.core.plan_gate.enforce_limit",
               new=AsyncMock(return_value=None)), \
         patch("app.services.product_service.ProductService.track_product",
               new=AsyncMock(return_value=None)):
        resp = await authed_client.post(f"/api/v1/products/{fake_id}/track")
    # Plan gate passed; product may not exist in test DB → 200 or 404
    assert resp.status_code in (200, 404)
