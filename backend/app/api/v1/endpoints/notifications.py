from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID
from app.core.database import get_db
from app.core.security import get_current_user, CurrentUser

router = APIRouter()


@router.get("/")
async def list_notifications(
    unread_only: Optional[bool] = None,
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """List notifications for the current user."""
    from sqlalchemy import select, desc
    from app.models.remaining_models import Notification
    q = (
        select(Notification)
        .where(Notification.user_id == user.user_id)
        .order_by(desc(Notification.created_at))
        .limit(limit)
    )
    if unread_only:
        q = q.where(Notification.is_read == False)
    result = await db.execute(q)
    notifs = result.scalars().all()
    return [
        {
            "id": str(n.id),
            "type": n.type,
            "title": n.title,
            "body": n.body,
            "action_url": n.action_url,
            "metadata": n.extra_data,
            "is_read": n.is_read,
            "created_at": n.created_at.isoformat() if n.created_at else None,
        }
        for n in notifs
    ]


@router.get("/unread-count")
async def unread_count(
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """Get count of unread notifications."""
    from sqlalchemy import select, func
    from app.models.remaining_models import Notification
    result = await db.execute(
        select(func.count()).where(
            Notification.user_id == user.user_id,
            Notification.is_read == False,
        )
    )
    count = result.scalar() or 0
    return {"count": count}


@router.post("/mark-read")
async def mark_all_read(
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """Mark all notifications as read."""
    from sqlalchemy import update
    from app.models.remaining_models import Notification
    await db.execute(
        update(Notification)
        .where(Notification.user_id == user.user_id)
        .values(is_read=True)
    )
    await db.commit()
    return {"message": "All notifications marked as read"}


@router.post("/{notification_id}/read")
async def mark_one_read(
    notification_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """Mark a single notification as read."""
    from sqlalchemy import update
    from app.models.remaining_models import Notification
    await db.execute(
        update(Notification)
        .where(
            Notification.id == notification_id,
            Notification.user_id == user.user_id,
        )
        .values(is_read=True)
    )
    await db.commit()
    return {"message": "Notification marked as read"}
