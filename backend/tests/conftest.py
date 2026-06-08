"""
Shared pytest fixtures for SellerVision AI backend tests.

Design decisions
----------------
- Tests run against an in-memory SQLite database (via aiosqlite) so no
  real Postgres instance is needed in CI. The few raw-SQL queries that use
  Postgres-specific syntax are mocked where needed.
- External services (Stripe, Resend, Anthropic) are always mocked.
- A seeded CurrentUser with owner role is injected by default; individual
  tests can override `get_current_user` to test different roles / scenarios.
"""

from __future__ import annotations

import asyncio
import os
import uuid
from datetime import datetime, timezone, timedelta
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

# ── Env overrides BEFORE importing the app ────────────────────────────────────
os.environ.update({
    "SECRET_KEY":        "test-secret-key-not-for-production",
    "DATABASE_URL":      "sqlite+aiosqlite:///:memory:",
    "REDIS_URL":         "redis://localhost:6379/0",
    "OPENAI_API_KEY":    "sk-test-fake",
    "ANTHROPIC_API_KEY": "test-fake",
    "STRIPE_SECRET_KEY": "sk_test_fake_key_for_tests",
    "CLERK_SECRET_KEY":  "",   # blank → dev bypass in get_current_user
    "RESEND_API_KEY":    "",   # blank → emails silently skipped
    "ADMIN_SECRET_KEY":  "test-admin-secret-abc123",
    "ENVIRONMENT":       "test",
})

# Patch Redis to avoid connection attempts in tests
_REDIS_PATCH = patch("app.core.cache.get_redis", new_callable=AsyncMock, return_value=None)
_REDIS_PATCH.start()

from app.main import app                          # noqa: E402 (imports after env setup)
from app.core.database import Base, get_db        # noqa: E402
from app.core.security import get_current_user    # noqa: E402

# ── In-memory SQLite engine ───────────────────────────────────────────────────
TEST_ENGINE = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False,
)
TestSession = async_sessionmaker(TEST_ENGINE, class_=AsyncSession, expire_on_commit=False)


# ── Session-scoped DB setup ───────────────────────────────────────────────────
@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    """Create all tables once per test session, tear down after."""
    async with TEST_ENGINE.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with TEST_ENGINE.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# ── Per-test DB session ───────────────────────────────────────────────────────
@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestSession() as session:
        yield session
        await session.rollback()


# ── Seed helpers ──────────────────────────────────────────────────────────────

OWNER_USER_ID  = str(uuid.uuid4())
OWNER_TENANT_ID = str(uuid.uuid4())
TENANT_SLUG     = "test-tenant"


async def seed_tenant(db: AsyncSession, *, plan_name: str = "Professional",
                       stripe_sub_id: str | None = None,
                       trial_ends_at: datetime | None = None,
                       is_active: bool = True) -> tuple:
    """Insert Plan + Tenant + TenantMember + User rows, return (user, tenant, plan)."""
    from decimal import Decimal
    from app.models.tenant import Plan, Tenant, TenantMember
    from app.models.user import User

    plan = Plan(
        id=uuid.uuid4(),
        name=plan_name,
        price_monthly=Decimal("149.00"),
        limits={"products": 100, "keywords": 5000, "api_calls": 100000, "users": 3, "agents": 5},
        features={"ai_analysis": True},
        is_active=True,
    )
    db.add(plan)

    tenant = Tenant(
        id=uuid.UUID(OWNER_TENANT_ID),
        slug=TENANT_SLUG,
        name="Test Tenant",
        plan_id=plan.id,
        stripe_subscription_id=stripe_sub_id,
        trial_ends_at=trial_ends_at,
        is_active=is_active,
    )
    db.add(tenant)

    user = User(
        id=uuid.UUID(OWNER_USER_ID),
        clerk_id="clerk_test_owner",
        email="owner@test.com",
        full_name="Test Owner",
        is_active=True,
    )
    db.add(user)
    db.add(TenantMember(
        tenant_id=tenant.id,
        user_id=user.id,
        role="owner",
    ))

    await db.commit()
    return user, tenant, plan


# ── CurrentUser mock ──────────────────────────────────────────────────────────

def make_mock_user(
    role: str = "owner",
    tenant_id: str = OWNER_TENANT_ID,
    tenant_slug: str = TENANT_SLUG,
) -> MagicMock:
    mock = MagicMock()
    mock.user_id   = OWNER_USER_ID
    mock.tenant_id = tenant_id
    mock.tenant_slug = tenant_slug
    mock.role = role
    mock.can.return_value = True
    mock.require = MagicMock()   # no-op by default
    return mock


# ── HTTP client fixture ────────────────────────────────────────────────────────
@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Unauthenticated client with DB override.
    Use `authed_client` for an owner-authenticated client.
    """
    async def _override_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def authed_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Client with owner-role CurrentUser injected."""
    mock_user = make_mock_user()

    async def _override_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_db
    app.dependency_overrides[get_current_user] = lambda: mock_user

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


# ── External-service mocks ─────────────────────────────────────────────────────
@pytest.fixture
def mock_stripe_checkout():
    """Mock stripe.checkout.Session.create → returns a fake checkout URL."""
    with patch("stripe.checkout.Session.create") as m:
        m.return_value = MagicMock(
            url="https://checkout.stripe.com/test_session_123",
            id="cs_test_123",
        )
        yield m


@pytest.fixture
def mock_stripe_portal():
    with patch("stripe.billing_portal.Session.create") as m:
        m.return_value = MagicMock(url="https://billing.stripe.com/portal_test")
        yield m


@pytest.fixture
def mock_anthropic():
    with patch("anthropic.AsyncAnthropic") as mock_cls:
        instance = AsyncMock()
        instance.messages.create.return_value = AsyncMock(
            content=[MagicMock(text=(
                '{"opportunity_score":80,"risk_score":25,"profit_score":72,'
                '"competition_score":55,"market_entry_score":68,'
                '"prediction_30d_units":120,"prediction_90d_units":380,'
                '"prediction_180d_units":800,"prediction_12m_revenue":48000,'
                '"reasoning":"Strong demand","action_recommendation":"Launch"}'
            ))]
        )
        mock_cls.return_value = instance
        yield instance
