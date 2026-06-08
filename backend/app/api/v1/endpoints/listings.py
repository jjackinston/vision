from fastapi import APIRouter, Depends, Query, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Any
from uuid import UUID
from app.core.database import get_db
from app.core.security import get_current_user, CurrentUser
from app.services.listing_service import ListingService

router = APIRouter()


class GenerateListingRequest(BaseModel):
    product_data: dict
    marketplace: str
    target_keywords: List[str] = []
    tone: str = "professional"


class GenerateMultiPlatformRequest(BaseModel):
    product_data: dict
    marketplaces: List[str]
    target_keywords: List[str] = []


@router.get("/")
async def list_listings(
    marketplace: Optional[str] = None,
    status: Optional[str] = None,
    min_seo_score: Optional[float] = None,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    service = ListingService()
    return await service.list_listings(user.tenant_slug, marketplace, status, min_seo_score)


@router.post("/generate")
async def generate_listing(
    body: GenerateListingRequest,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """Module 9: AI listing builder for any marketplace."""
    user.require("write")
    service = ListingService()
    return await service.generate_ai_listing(body.product_data, body.marketplace, body.target_keywords, body.tone)


@router.post("/generate-multi-platform")
async def generate_multi_platform(
    body: GenerateMultiPlatformRequest,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """Module 9 + 15: Generate optimized listing for all platforms at once."""
    user.require("write")
    service = ListingService()
    return await service.generate_multi_platform_listings(body.product_data, body.marketplaces, body.target_keywords)


@router.post("/{listing_id}/publish")
async def publish_listing(
    listing_id: UUID,
    marketplace: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """Module 15: Push listing live to marketplace."""
    user.require("write")
    service = ListingService()
    background_tasks.add_task(service.sync_listing_to_marketplace, str(listing_id), marketplace, user.tenant_slug)
    return {"message": "Publish queued", "listing_id": str(listing_id), "marketplace": marketplace}


@router.post("/{listing_id}/optimize")
async def optimize_listing(
    listing_id: UUID,
    marketplace: str,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """AI re-optimize an existing listing."""
    user.require("write")
    service = ListingService()
    return await service.optimize_existing_listing(str(listing_id), marketplace, user.tenant_slug)


@router.get("/{listing_id}/seo-audit")
async def seo_audit(
    listing_id: UUID,
    marketplace: str,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    service = ListingService()
    return await service.audit_seo(str(listing_id), marketplace, user.tenant_slug)
