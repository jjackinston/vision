"""Module 23: SellerVision Marketplace â€” buy/sell dashboards, agents, prompts, templates."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID
from app.core.database import get_db
from app.core.security import get_current_user, CurrentUser

router = APIRouter()


@router.get("/assets")
async def list_assets(
    type: Optional[str] = None,
    sort_by: str = Query("downloads", pattern="^(downloads|rating|price|created_at)$"),
    price_max: Optional[float] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """Browse the SellerVision Marketplace."""
    from sqlalchemy import select, desc
    from app.models.remaining_models import MarketplaceAsset
    q = select(MarketplaceAsset).where(MarketplaceAsset.is_published == True)
    if type:
        q = q.where(MarketplaceAsset.type == type)
    if price_max is not None:
        q = q.where(MarketplaceAsset.price <= price_max)
    if search:
        from sqlalchemy import or_
        q = q.where(or_(
            MarketplaceAsset.name.ilike(f"%{search}%"),
            MarketplaceAsset.description.ilike(f"%{search}%"),
        ))
    sort_col = getattr(MarketplaceAsset, sort_by, MarketplaceAsset.downloads)
    q = q.order_by(desc(sort_col)).limit(50)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/assets")
async def publish_asset(
    asset: dict,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """Publish a new asset to the marketplace."""
    user.require("write")
    from app.models.remaining_models import MarketplaceAsset
    new_asset = MarketplaceAsset(**asset, creator_id=user.user_id)
    db.add(new_asset)
    await db.commit()
    await db.refresh(new_asset)
    return new_asset


@router.get("/assets/{asset_id}")
async def get_asset(
    asset_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    from sqlalchemy import select
    from app.models.remaining_models import MarketplaceAsset
    result = await db.execute(select(MarketplaceAsset).where(MarketplaceAsset.id == asset_id))
    asset = result.scalar_one_or_none()
    if not asset:
        from fastapi import HTTPException
        raise HTTPException(404, "Asset not found")
    return asset


@router.post("/assets/{asset_id}/purchase")
async def purchase_asset(
    asset_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """Purchase and install an asset."""
    from app.services.marketplace_service import MarketplaceService
    service = MarketplaceService(db, user.tenant_slug)
    return await service.purchase_asset(str(asset_id), user.user_id)


@router.get("/my-assets")
async def my_assets(
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """Assets created or purchased by current user."""
    from sqlalchemy import select
    from app.models.remaining_models import MarketplaceAsset
    result = await db.execute(
        select(MarketplaceAsset).where(MarketplaceAsset.creator_id == user.user_id)
    )
    return result.scalars().all()


@router.get("/featured")
async def featured_assets(db: AsyncSession = Depends(get_db)):
    """Curated featured assets â€” no auth required."""
    return FEATURED_ASSETS


FEATURED_ASSETS = [
    {"name": "Amazon BSR Tracker Dashboard", "type": "dashboard", "price": 0, "downloads": 1240, "rating": 4.8},
    {"name": "Mega Keyword Research Prompt Pack (500 prompts)", "type": "prompt", "price": 19.99, "downloads": 890, "rating": 4.9},
    {"name": "AI PPC Optimizer Agent Config", "type": "agent", "price": 49.99, "downloads": 340, "rating": 4.7},
    {"name": "Product Launch Automation Workflow", "type": "automation", "price": 29.99, "downloads": 520, "rating": 4.6},
    {"name": "Competitor Intelligence Template", "type": "template", "price": 0, "downloads": 2100, "rating": 4.5},
]
