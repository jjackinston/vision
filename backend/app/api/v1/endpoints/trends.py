from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from pydantic import BaseModel
from app.core.database import get_db
from app.core.security import get_current_user, CurrentUser
from app.services.trend_service import TrendService


class TrendDetectRequest(BaseModel):
    category: str
    sources: List[str] = ["google", "tiktok", "reddit", "pinterest", "amazon"]
    lookback_days: int = 30

router = APIRouter()


@router.get("/")
async def list_trends(
    category: Optional[str] = None,
    source: Optional[str] = None,
    min_score: float = Query(0, ge=0, le=100),
    limit: int = Query(20, le=100),
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    service = TrendService(db, user.tenant_slug)
    return await service.list_trends(category, source, min_score, limit)


@router.post("/detect")
async def detect_trends(
    request: TrendDetectRequest,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """Module 14: Real-time trend detection across all sources."""
    user.require("write")
    service = TrendService(db, user.tenant_slug)
    return await service.detect_trends(request.category, request.sources, request.lookback_days)


@router.get("/emerging")
async def emerging_trends(
    limit: int = Query(10, le=50),
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """Get emerging trends detected in last 48 hours."""
    service = TrendService(db, user.tenant_slug)
    return await service.get_emerging(limit)


@router.get("/viral")
async def viral_products(
    marketplace: str = "tiktok",
    limit: int = Query(20, le=50),
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """Products going viral right now."""
    service = TrendService(db, user.tenant_slug)
    return await service.get_viral_products(marketplace, limit)


@router.get("/{trend_id}/prediction")
async def trend_prediction(
    trend_id: str,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """Predict trend lifespan, peak, and commercial potential."""
    service = TrendService(db, user.tenant_slug)
    return await service.predict_trend(trend_id)
