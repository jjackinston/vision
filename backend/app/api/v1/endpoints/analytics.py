from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.core.database import get_db
from app.core.security import get_current_user, CurrentUser
from app.core.plan_gate import require_plan
from app.services.analytics_service import AnalyticsService
from app.services.ceo_dashboard_service import CEODashboardService, DigitalTwinService

router = APIRouter()


@router.get("/overview")
async def get_overview(
    period: str = Query("30d", pattern="^(7d|30d|90d|1y)$"),
    marketplace: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    service = AnalyticsService(db, user.tenant_slug)
    return await service.get_overview(period, marketplace)


@router.get("/revenue")
async def get_revenue(
    period: str = Query("30d"),
    group_by: str = Query("day", pattern="^(day|week|month)$"),
    marketplace: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    service = AnalyticsService(db, user.tenant_slug)
    return await service.get_revenue_series(period, group_by, marketplace)


@router.get("/profit")
async def get_profit_breakdown(
    period: str = Query("30d"),
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    service = AnalyticsService(db, user.tenant_slug)
    return await service.get_profit_breakdown(period)


@router.get("/by-product")
async def get_analytics_by_product(
    period: str = Query("30d"),
    limit: int = Query(20, le=100),
    sort_by: str = Query("revenue"),
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    service = AnalyticsService(db, user.tenant_slug)
    return await service.get_by_product(period, limit, sort_by)


@router.get("/by-platform")
async def get_analytics_by_platform(
    period: str = Query("30d"),
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    service = AnalyticsService(db, user.tenant_slug)
    return await service.get_by_platform(period)


@router.get("/ceo-recommendations")
async def ceo_recommendations(
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    service = CEODashboardService(db=db)
    return await service.get_daily_recommendations(user.tenant_id)


@router.get("/executive-summary")
async def executive_summary(
    period: str = Query("week"),
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    service = CEODashboardService(db=db)
    return await service.get_executive_summary(user.tenant_id, period)


@router.post("/simulate")
async def simulate_scenario(
    scenario_type: str,
    parameters: dict,
    forecast_months: int = Query(6, le=24),
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(require_plan("business")),
):
    """Module 19: Digital Twin -- what-if simulation. Requires Business plan or higher."""
    service = DigitalTwinService(db=db)
    return await service.simulate(user.tenant_id, scenario_type, parameters, forecast_months)


@router.get("/product-metrics")
async def get_product_metrics(
    product_id: Optional[str] = None,
    days: int = Query(30, le=365),
    marketplace: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """Time-series BSR, review count, and revenue metrics per product."""
    from datetime import datetime, timedelta
    from sqlalchemy import select, desc
    from app.models.product import ProductMetric
    from uuid import UUID

    cutoff = datetime.utcnow() - timedelta(days=days)
    q = select(ProductMetric).where(ProductMetric.time >= cutoff).order_by(desc(ProductMetric.time))
    if product_id:
        q = q.where(ProductMetric.product_id == UUID(product_id))
    if marketplace:
        q = q.where(ProductMetric.marketplace == marketplace)
    result = await db.execute(q.limit(500))
    rows = result.scalars().all()
    return [
        {
            "id": str(r.id),
            "time": r.time.isoformat(),
            "product_id": str(r.product_id),
            "marketplace": r.marketplace,
            "price": float(r.price) if r.price else None,
            "bsr_rank": r.bsr_rank,
            "bsr_category": r.bsr_category,
            "review_count": r.review_count,
            "review_rating": float(r.review_rating) if r.review_rating else None,
            "estimated_sales": r.estimated_sales,
            "estimated_revenue": float(r.estimated_revenue) if r.estimated_revenue else None,
        }
        for r in rows
    ]


@router.get("/keyword-metrics")
async def get_keyword_metrics(
    keyword_id: Optional[str] = None,
    days: int = Query(30, le=365),
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """Time-series search volume and CPC per keyword."""
    from datetime import datetime, timedelta
    from sqlalchemy import select, desc
    from app.models.keyword import KeywordMetric
    from uuid import UUID

    cutoff = datetime.utcnow() - timedelta(days=days)
    q = select(KeywordMetric).where(KeywordMetric.time >= cutoff).order_by(desc(KeywordMetric.time))
    if keyword_id:
        q = q.where(KeywordMetric.keyword_id == UUID(keyword_id))
    result = await db.execute(q.limit(500))
    rows = result.scalars().all()
    return [
        {
            "id": str(r.id),
            "time": r.time.isoformat(),
            "keyword_id": str(r.keyword_id),
            "search_volume": r.search_volume,
            "cpc": float(r.cpc) if r.cpc else None,
            "ranking_products": r.ranking_products,
            "sponsored_count": r.sponsored_count,
        }
        for r in rows
    ]


@router.get("/profit-calculator")
async def profit_calculator(
    product_cost: float,
    selling_price: float,
    marketplace: str,
    monthly_units: int = 0,
    ad_spend_daily: float = 0,
    shipping_cost: float = 0,
    category: str = "home",
):
    """Module 17: Real-time profit calculation -- no auth required."""
    from app.services.profit_calculator import ProfitCalculator
    calc = ProfitCalculator()
    return calc.calculate({
        "product_cost": product_cost,
        "selling_price": selling_price,
        "marketplace": marketplace,
        "monthly_units": monthly_units,
        "ad_spend_daily": ad_spend_daily,
        "shipping_cost": shipping_cost,
        "category": category,
    })


@router.get("/platform-comparison")
async def compare_platforms(
    product_cost: float,
    selling_price: float,
    monthly_units: int = 100,
    category: str = "home",
):
    """Compare profitability across all platforms."""
    from app.services.profit_calculator import ProfitCalculator
    calc = ProfitCalculator()
    return calc.compare_platforms(product_cost, selling_price, monthly_units, category)
