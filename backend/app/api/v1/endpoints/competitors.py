from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID
from app.core.database import get_db
from app.core.security import get_current_user, CurrentUser
from app.services.competitor_service import CompetitorService

router = APIRouter()


@router.get("/")
async def list_competitors(
    product_id: Optional[UUID] = None,
    marketplace: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    service = CompetitorService(db, user.tenant_slug)
    return await service.list_competitors(product_id, marketplace)


@router.post("/track")
async def track_competitor(
    asin: str,
    marketplace: str = "amazon",
    product_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    user.require("write")
    service = CompetitorService(db, user.tenant_slug)
    return await service.track_competitor(asin, marketplace, str(product_id) if product_id else None)


@router.post("/weakness-scan")
async def weakness_scan(
    asin: str,
    marketplace: str = "amazon",
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """Module 4: Deep review mining for competitor weaknesses."""
    from app.services.ai_product_service import AIProductService
    ai_service = AIProductService()
    return await ai_service.scan_competitor_weaknesses({"asin": asin, "marketplace": marketplace})


@router.get("/{competitor_id}/price-history")
async def price_history(
    competitor_id: UUID,
    days: int = Query(30, le=365),
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    service = CompetitorService(db, user.tenant_slug)
    return await service.get_price_history(competitor_id, days)


@router.get("/{competitor_id}/threat-analysis")
async def threat_analysis(
    competitor_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    service = CompetitorService(db, user.tenant_slug)
    return await service.analyze_threat(competitor_id)


@router.get("/market-overview")
async def market_overview(
    category: str,
    marketplace: str = "amazon",
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    service = CompetitorService(db, user.tenant_slug)
    return await service.get_market_overview(category, marketplace)
