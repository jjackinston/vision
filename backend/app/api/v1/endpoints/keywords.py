from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from uuid import UUID

from app.core.database import get_db
from app.core.security import get_current_user, CurrentUser, require_subscription
from app.services.keyword_service import KeywordService
from app.schemas.keyword import (
    KeywordResearchResponse, KeywordClusterResponse,
    KeywordBulkRequest, ReverseASINResponse,
)

router = APIRouter()


@router.get("/research")
async def research_keyword(
    q: str = Query(..., min_length=1),
    marketplace: str = Query("amazon"),
    include_related: bool = True,
    include_long_tail: bool = True,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """Module 8: Full keyword intelligence â€” volume, CPC, difficulty, intent, related."""
    service = KeywordService(db, user.tenant_slug)
    return await service.research_keyword(q, marketplace, include_related, include_long_tail)


@router.post("/bulk")
async def research_bulk(
    request: KeywordBulkRequest,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(require_subscription()),
):
    """Research up to 100 keywords at once — blocked at plan keyword limit."""
    from app.services.billing_service import BillingService
    billing = BillingService(db)
    usage = await billing.get_usage(user.tenant_id)
    limit = usage.get("keywords_limit", 0)
    if limit > 0 and usage.get("keywords_researched", 0) >= limit:
        raise HTTPException(
            status_code=402,
            detail=f"Keyword limit reached ({limit}). Upgrade your plan at /settings?section=billing",
        )
    service = KeywordService(db, user.tenant_slug)
    return await service.research_bulk(request.keywords, request.marketplace)


@router.post("/cluster")
async def cluster_keywords(
    keywords: List[str],
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """Cluster keywords by semantic topic."""
    service = KeywordService(db, user.tenant_slug)
    return await service.cluster_keywords(keywords)


@router.get("/reverse-asin/{asin}", response_model=ReverseASINResponse)
async def reverse_asin(
    asin: str,
    marketplace: str = Query("amazon"),
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """Get all keywords an ASIN ranks for (organic + sponsored)."""
    service = KeywordService(db, user.tenant_slug)
    return await service.reverse_asin_lookup(asin, marketplace)


@router.get("/opportunities")
async def keyword_opportunities(
    category: Optional[str] = None,
    min_volume: int = Query(1000, ge=0),
    max_difficulty: float = Query(60.0, le=100),
    marketplace: str = "amazon",
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """Find low-competition, high-volume keyword opportunities."""
    service = KeywordService(db, user.tenant_slug)
    return await service.find_opportunities(category, min_volume, max_difficulty, marketplace)


@router.get("/trending")
async def trending_keywords(
    marketplace: str = "amazon",
    period: str = Query("7d", pattern="^(24h|7d|30d)$"),
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    service = KeywordService(db, user.tenant_slug)
    return await service.get_trending_keywords(marketplace, period)


@router.get("/{keyword_id}/history")
async def keyword_history(
    keyword_id: UUID,
    days: int = Query(90, le=365),
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    service = KeywordService(db, user.tenant_slug)
    return await service.get_keyword_history(keyword_id, days)
