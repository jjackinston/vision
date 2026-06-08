from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID
from app.core.database import get_db
from app.core.security import get_current_user, CurrentUser
from app.services.ppc_service import PPCService

router = APIRouter()


@router.get("/campaigns")
async def list_campaigns(
    marketplace: Optional[str] = None,
    status: Optional[str] = None,
    high_acos_only: bool = False,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    service = PPCService(db, user.tenant_slug)
    return await service.list_campaigns(marketplace, status, high_acos_only)


@router.get("/performance")
async def get_performance(
    days: int = Query(30, le=365),
    marketplace: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    service = PPCService(db, user.tenant_slug)
    return await service.get_performance_summary(user.tenant_id, days)


@router.get("/ai-recommendations")
async def ai_recommendations(
    optimization_goal: str = Query("acos", pattern="^(acos|roas|rank|revenue)$"),
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """AI-powered PPC optimization recommendations."""
    service = PPCService(db, user.tenant_slug)
    return await service.get_ai_recommendations(user.tenant_id, optimization_goal)


@router.post("/campaigns/{campaign_id}/optimize")
async def optimize_campaign(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    user.require("write")
    service = PPCService(db, user.tenant_slug)
    return await service.optimize_campaign(str(campaign_id))


@router.get("/keyword-harvesting")
async def keyword_harvesting(
    campaign_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """Find converting search terms to add as keywords."""
    service = PPCService(db, user.tenant_slug)
    return await service.get_harvest_suggestions(str(campaign_id) if campaign_id else None)


@router.get("/negative-keywords")
async def negative_keyword_suggestions(
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """Find wasted spend keywords to negate."""
    service = PPCService(db, user.tenant_slug)
    return await service.get_negative_suggestions()
