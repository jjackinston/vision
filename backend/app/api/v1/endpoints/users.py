from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_user, CurrentUser

router = APIRouter()


@router.get("/me")
async def get_profile(
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    from sqlalchemy import select
    from app.models.user import User
    result = await db.execute(select(User).where(User.id == user.user_id))
    return result.scalar_one_or_none()


@router.put("/me")
async def update_profile(
    full_name: str = None,
    avatar_url: str = None,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    from sqlalchemy import update
    from app.models.user import User
    updates = {}
    if full_name:
        updates["full_name"] = full_name
    if avatar_url:
        updates["avatar_url"] = avatar_url
    if updates:
        await db.execute(update(User).where(User.id == user.user_id).values(**updates))
        await db.commit()
    return {"updated": True}


@router.get("/me/notifications")
async def get_notifications(
    unread_only: bool = False,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    from sqlalchemy import select, desc
    from app.models.remaining_models import Notification
    q = select(Notification).where(Notification.user_id == user.user_id).order_by(desc(Notification.created_at)).limit(limit)
    if unread_only:
        q = q.where(Notification.is_read == False)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/me/notifications/mark-read")
async def mark_notifications_read(
    notification_ids: list[str] = None,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    from sqlalchemy import update
    from app.models.remaining_models import Notification
    q = update(Notification).where(Notification.user_id == user.user_id).values(is_read=True)
    if notification_ids:
        q = q.where(Notification.id.in_(notification_ids))
    await db.execute(q)
    await db.commit()
    return {"marked_read": len(notification_ids) if notification_ids else "all"}
