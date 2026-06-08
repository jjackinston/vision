from sqlalchemy.ext.asyncio import AsyncSession
from app.models.remaining_models import Notification
from app.core.database import AsyncSessionLocal
import logging

logger = logging.getLogger(__name__)


async def send_notification(
    tenant_id: str,
    title: str,
    body: str = None,
    action_url: str = None,
    notification_type: str = "info",
    metadata: dict = None,
) -> None:
    """Send in-app notification to all users in a tenant."""
    async with AsyncSessionLocal() as db:
        from sqlalchemy import select
        from app.models.tenant import TenantMember
        from app.models.user import User
        result = await db.execute(
            select(TenantMember.user_id).where(TenantMember.tenant_id == tenant_id)
        )
        user_ids = [row.user_id for row in result.fetchall()]
        for user_id in user_ids:
            notification = Notification(
                user_id=user_id,
                type=notification_type,
                title=title,
                body=body,
                action_url=action_url,
                metadata=metadata or {},
            )
            db.add(notification)
        await db.commit()
        logger.info(f"Sent notification '{title}' to {len(user_ids)} users in tenant {tenant_id}")


async def send_stockout_alert(tenant_id: str, product_name: str, days_remaining: int) -> None:
    await send_notification(
        tenant_id=tenant_id,
        title=f"⚠️ Stockout Warning: {product_name}",
        body=f"Only {days_remaining} days of inventory remaining. Reorder immediately.",
        action_url="/inventory",
        notification_type="critical",
        metadata={"days_remaining": days_remaining},
    )


async def send_opportunity_alert(tenant_id: str, product_name: str, score: float) -> None:
    await send_notification(
        tenant_id=tenant_id,
        title=f"🚀 New Opportunity: {product_name}",
        body=f"Opportunity score {score:.0f}/100 detected. Review now.",
        action_url="/products",
        notification_type="opportunity",
        metadata={"score": score},
    )


async def send_ppc_alert(tenant_id: str, campaign_name: str, acos: float) -> None:
    await send_notification(
        tenant_id=tenant_id,
        title=f"📊 High ACoS Alert: {campaign_name}",
        body=f"ACoS is at {acos:.1f}% — above your 25% target. AI recommendations ready.",
        action_url="/ppc",
        notification_type="warning",
    )
