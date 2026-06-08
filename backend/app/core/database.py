from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text, event
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,        # verify connection health before each checkout
    pool_recycle=1800,         # recycle connections every 30 min (avoids idle-timeout drops)
    pool_timeout=30,           # raise if no connection available within 30 s
    echo=settings.DEBUG,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def set_tenant_context(session: AsyncSession, tenant_slug: str) -> None:
    """Set PostgreSQL search_path to tenant schema for RLS."""
    await session.execute(
        text(f"SET search_path TO tenant_{tenant_slug}, public")
    )


@asynccontextmanager
async def tenant_session(tenant_slug: str) -> AsyncGenerator[AsyncSession, None]:
    """Session with tenant schema context."""
    async with AsyncSessionLocal() as session:
        await set_tenant_context(session, tenant_slug)
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def create_tenant_schema(tenant_slug: str) -> None:
    """Create isolated PostgreSQL schema for new tenant."""
    async with AsyncSessionLocal() as session:
        await session.execute(text(f"SELECT create_tenant_schema('{tenant_slug}')"))
        await session.commit()
        logger.info(f"Created schema for tenant: {tenant_slug}")
