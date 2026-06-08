from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.tenant import Tenant


async def get_all_active_tenants() -> list[Tenant]:
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Tenant).where(Tenant.is_active == True))
        return result.scalars().all()


async def get_tenant_by_slug(slug: str) -> Tenant | None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Tenant).where(Tenant.slug == slug))
        return result.scalar_one_or_none()
