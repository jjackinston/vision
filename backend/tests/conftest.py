import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from unittest.mock import AsyncMock, patch
import os

os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing-only-do-not-use-in-prod")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://postgres:testpassword@localhost:5432/sellervision_test")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("ANTHROPIC_API_KEY", "test-key")
os.environ.setdefault("STRIPE_SECRET_KEY", "sk_test_fake")
os.environ.setdefault("CLERK_SECRET_KEY", "test-clerk-key")

from app.main import app
from app.core.database import Base, get_db

TEST_DB_URL = "postgresql+asyncpg://postgres:testpassword@localhost:5432/sellervision_test"
test_engine = create_async_engine(TEST_DB_URL, echo=False)
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session():
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    mock_user = AsyncMock()
    mock_user.user_id = "test-user-id"
    mock_user.tenant_id = "test-tenant-id"
    mock_user.tenant_slug = "test-tenant"
    mock_user.role = "owner"
    mock_user.can.return_value = True
    mock_user.require = lambda _: None

    from app.core.security import get_current_user
    app.dependency_overrides[get_current_user] = lambda: mock_user

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture
def mock_anthropic():
    with patch("anthropic.AsyncAnthropic") as mock:
        mock_instance = AsyncMock()
        mock_instance.messages.create.return_value = AsyncMock(
            content=[AsyncMock(text='{"opportunity_score": 80, "risk_score": 25, '
                               '"profit_score": 72, "competition_score": 55, '
                               '"market_entry_score": 68, "prediction_30d_units": 120, '
                               '"prediction_90d_units": 380, "prediction_180d_units": 800, '
                               '"prediction_12m_revenue": 48000, '
                               '"reasoning": "Strong demand signal", '
                               '"action_recommendation": "Launch immediately"}')]
        )
        mock.return_value = mock_instance
        yield mock_instance
