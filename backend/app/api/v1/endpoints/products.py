from fastapi import APIRouter, Depends, Query, BackgroundTasks, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from uuid import UUID

from app.core.database import get_db
from app.core.security import get_current_user, CurrentUser, require_subscription
from app.schemas.product import (
    ProductCreate, ProductResponse, ProductListResponse,
    ProductOpportunityScore, ProductSearchRequest, ProductSuccessPrediction,
    SaturationRadar, LaunchSimulatorInput, LaunchSimulatorResult,
)
from app.services.product_service import ProductService
from app.services.ai_product_service import AIProductService
from app.workers.tasks import analyze_product_task

router = APIRouter()


@router.get("/", response_model=ProductListResponse)
async def list_products(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    marketplace: Optional[str] = None,
    is_tracked: Optional[bool] = None,
    min_opportunity: Optional[float] = None,
    sort_by: str = Query("opportunity_score", enum=["opportunity_score", "revenue", "created_at"]),
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    service = ProductService(db, user.tenant_slug)
    return await service.list_products(
        page=page,
        per_page=per_page,
        marketplace=marketplace,
        is_tracked=is_tracked,
        min_opportunity=min_opportunity,
        sort_by=sort_by,
    )


@router.post("/search", response_model=List[ProductResponse])
async def search_products(
    request: ProductSearchRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """Search and analyze products across marketplaces."""
    user.require("write")
    service = ProductService(db, user.tenant_slug)
    ai_service = AIProductService()
    products = await service.search_products(request)
    # Queue deep AI analysis in background (gracefully skip if Celery/Redis unavailable)
    for p in products:
        try:
            background_tasks.add_task(analyze_product_task.delay, str(p.id), user.tenant_slug)
        except Exception:
            pass  # Redis not running — search still returns results
    return products


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    service = ProductService(db, user.tenant_slug)
    product = await service.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/{product_id}/track")
async def track_product(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(require_subscription()),
):
    """Track a product — blocked when plan limit is reached or subscription is past-due."""
    user.require("write")
    service = ProductService(db, user.tenant_slug)
    # enforce_limit is called inside track_product when tenant_id is passed
    await service.track_product(product_id, tenant_id=user.tenant_id)
    return {"message": "Product tracking enabled", "product_id": str(product_id)}


@router.get("/{product_id}/opportunity-score", response_model=ProductOpportunityScore)
async def get_opportunity_score(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """Get AI-generated opportunity scores and predictions."""
    ai_service = AIProductService()
    service = ProductService(db, user.tenant_slug)
    product = await service.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return await ai_service.calculate_opportunity_score(product)


@router.post("/predict-success", response_model=ProductSuccessPrediction)
async def predict_product_success(
    concept: dict,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """MODULE 2: Predict probability of product success before launch."""
    user.require("write")
    ai_service = AIProductService()
    return await ai_service.predict_success(concept)


@router.post("/saturation-radar", response_model=SaturationRadar)
async def get_saturation_radar(
    category: str,
    marketplace: str = "amazon",
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """MODULE 3: Predict future market saturation."""
    ai_service = AIProductService()
    return await ai_service.analyze_saturation(category, marketplace)


@router.post("/launch-simulator", response_model=LaunchSimulatorResult)
async def simulate_launch(
    input_data: LaunchSimulatorInput,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """MODULE 10: Simulate product launch before spending money."""
    user.require("write")
    ai_service = AIProductService()
    return await ai_service.simulate_launch(input_data)


@router.get("/{product_id}/reverse-asin")
async def reverse_asin_lookup(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """Get all keywords a product ranks for."""
    service = ProductService(db, user.tenant_slug)
    return await service.reverse_asin_lookup(product_id)


@router.get("/{product_id}/competitor-weaknesses")
async def get_competitor_weaknesses(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """MODULE 4: Analyze competitor weaknesses via review mining."""
    ai_service = AIProductService()
    service = ProductService(db, user.tenant_slug)
    product = await service.get_product(product_id)
    return await ai_service.scan_competitor_weaknesses(product)


@router.post("/ai-create")
async def ai_create_product(
    category: str,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """MODULE 5: Use AI to invent better products from market gap analysis."""
    user.require("write")
    ai_service = AIProductService()
    return await ai_service.create_product_concept(category)


@router.get("/{product_id}/cross-platform", response_model=dict)
async def cross_platform_comparison(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """MODULE 6 & 7: Compare product across all platforms + recommend best."""
    service = ProductService(db, user.tenant_slug)
    ai_service = AIProductService()
    product = await service.get_product(product_id)
    comparison = await service.get_cross_platform_data(product)
    recommendation = await ai_service.recommend_best_platform(product, comparison)
    return {"comparison": comparison, "recommendation": recommendation}
