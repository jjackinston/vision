import re
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.user import User
from app.models.tenant import Tenant, TenantMember


def _make_slug(email: str, full_name: str) -> str:
    """Derive a unique-ish tenant slug from email prefix."""
    base = email.split("@")[0] if "@" in email else (full_name or "seller")
    slug = re.sub(r"[^a-z0-9]+", "-", base.lower()).strip("-")[:60] or "seller"
    return slug


async def get_user_by_clerk_id(db: AsyncSession, clerk_id: str) -> User | None:
    result = await db.execute(select(User).where(User.clerk_id == clerk_id))
    return result.scalar_one_or_none()


async def get_tenant_member(db: AsyncSession, user_id, tenant_id) -> TenantMember | None:
    result = await db.execute(
        select(TenantMember).where(TenantMember.user_id == user_id, TenantMember.tenant_id == tenant_id)
    )
    return result.scalar_one_or_none()


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def sync_clerk_user(self, clerk_data: dict) -> User:
        clerk_id = clerk_data.get("id")
        email = (clerk_data.get("email_addresses") or [{}])[0].get("email_address", "")
        full_name = f"{clerk_data.get('first_name', '')} {clerk_data.get('last_name', '')}".strip()
        avatar_url = clerk_data.get("image_url")

        existing = await get_user_by_clerk_id(self.db, clerk_id)
        if existing:
            await self.db.execute(
                update(User).where(User.clerk_id == clerk_id)
                .values(email=email, full_name=full_name, avatar_url=avatar_url)
            )
            await self.db.commit()
            return existing

        # Create user
        user = User(clerk_id=clerk_id, email=email, full_name=full_name, avatar_url=avatar_url)
        self.db.add(user)
        await self.db.flush()  # get user.id before commit

        # Auto-provision tenant + owner membership for new user
        base_slug = _make_slug(email, full_name)
        # Ensure slug uniqueness by appending a short suffix if needed
        slug = base_slug
        counter = 1
        while True:
            exists = await self.db.scalar(select(Tenant.id).where(Tenant.slug == slug))
            if not exists:
                break
            slug = f"{base_slug}-{counter}"
            counter += 1

        tenant = Tenant(
            slug=slug,
            name=full_name or email.split("@")[0] or "My Store",
        )
        self.db.add(tenant)
        await self.db.flush()  # get tenant.id

        member = TenantMember(tenant_id=tenant.id, user_id=user.id, role="owner")
        self.db.add(member)

        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update_clerk_user(self, clerk_data: dict) -> None:
        clerk_id = clerk_data.get("id")
        email = (clerk_data.get("email_addresses") or [{}])[0].get("email_address", "")
        full_name = f"{clerk_data.get('first_name', '')} {clerk_data.get('last_name', '')}".strip()
        await self.db.execute(
            update(User).where(User.clerk_id == clerk_id)
            .values(email=email, full_name=full_name)
        )
        await self.db.commit()

    async def deactivate_user(self, clerk_id: str) -> None:
        await self.db.execute(
            update(User).where(User.clerk_id == clerk_id).values(is_active=False)
        )
        await self.db.commit()
