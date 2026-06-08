"""Analytics aggregation service for dashboards and reporting.

Performance notes:
- All read methods are cached in Redis keyed by tenant + params.
- TTL: 300 s (5 min) for live dashboards; 3600 s (1 h) for historical reports.
- Cache is busted by calling invalidate_tenant_cache(tenant_slug, "analytics").
"""
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from app.core.cache import cache_get, cache_set, make_cache_key


class AnalyticsService:
    def __init__(self, db: AsyncSession, tenant_slug: str):
        self.db = db
        self.tenant_slug = tenant_slug

    # ── Helpers ────────────────────────────────────────────────────────

    @staticmethod
    def _period_to_days(period: str) -> int:
        return {"7d": 7, "30d": 30, "90d": 90, "1y": 365}.get(period, 30)

    # ── Overview ───────────────────────────────────────────────────────

    async def get_overview(self, period: str, marketplace: Optional[str] = None) -> dict:
        key = make_cache_key(self.tenant_slug, "analytics:overview", period, marketplace or "all")
        hit = await cache_get(key)
        if hit is not None:
            return hit

        days = self._period_to_days(period)
        cutoff = datetime.utcnow() - timedelta(days=days)
        prev_cutoff = cutoff - timedelta(days=days)

        from app.models.remaining_models import SalesAnalytic

        def _base_q():
            q = select(
                func.sum(SalesAnalytic.gross_revenue).label("revenue"),
                func.sum(SalesAnalytic.net_profit).label("profit"),
                func.sum(SalesAnalytic.units_sold).label("units"),
                func.sum(SalesAnalytic.orders).label("orders"),
                func.sum(SalesAnalytic.ad_spend).label("ad_spend"),
            )
            if marketplace:
                q = q.where(SalesAnalytic.marketplace == marketplace)
            return q

        current = (await self.db.execute(_base_q().where(SalesAnalytic.time >= cutoff))).one()
        prev = (await self.db.execute(
            _base_q().where(SalesAnalytic.time >= prev_cutoff, SalesAnalytic.time < cutoff)
        )).one()

        def pct(curr, prev_val):
            if not prev_val:
                return 0
            return round((curr - prev_val) / prev_val * 100, 1)

        revenue = float(current.revenue or 0)
        prev_revenue = float(prev.revenue or 0)
        profit = float(current.profit or 0)
        ad_spend = float(current.ad_spend or 0)

        result = {
            "period": period,
            "revenue": revenue,
            "revenue_change": pct(revenue, prev_revenue),
            "profit": profit,
            "profit_change": pct(profit, float(prev.profit or 0)),
            "units_sold": int(current.units or 0),
            "orders": int(current.orders or 0),
            "ad_spend": ad_spend,
            "acos": round(ad_spend / revenue * 100, 1) if revenue > 0 else 0,
            "tacos": round(ad_spend / revenue * 100, 1) if revenue > 0 else 0,
            "roi": round(profit / max(revenue - profit, 1) * 100, 1) if revenue > 0 else 0,
        }
        await cache_set(key, result, ttl=300)
        return result

    # ── Revenue series ─────────────────────────────────────────────────

    async def get_revenue_series(self, period: str, group_by: str, marketplace: Optional[str]) -> list:
        key = make_cache_key(self.tenant_slug, "analytics:revenue", period, group_by, marketplace or "all")
        hit = await cache_get(key)
        if hit is not None:
            return hit

        days = self._period_to_days(period)
        cutoff = datetime.utcnow() - timedelta(days=days)
        from app.models.remaining_models import SalesAnalytic

        trunc_fn = {"day": "day", "week": "week", "month": "month"}.get(group_by, "day")
        q = (
            select(
                func.date_trunc(trunc_fn, SalesAnalytic.time).label("date"),
                func.sum(SalesAnalytic.gross_revenue).label("revenue"),
                func.sum(SalesAnalytic.net_profit).label("profit"),
                func.sum(SalesAnalytic.ad_spend).label("ad_spend"),
                func.sum(SalesAnalytic.units_sold).label("units"),
            )
            .where(SalesAnalytic.time >= cutoff)
            .group_by("date")
            .order_by("date")
        )
        if marketplace:
            q = q.where(SalesAnalytic.marketplace == marketplace)

        rows = (await self.db.execute(q)).all()
        result = [
            {"date": str(r.date), "revenue": float(r.revenue or 0),
             "profit": float(r.profit or 0), "ad_spend": float(r.ad_spend or 0),
             "units": int(r.units or 0)}
            for r in rows
        ]
        await cache_set(key, result, ttl=300)
        return result

    # ── Profit breakdown ───────────────────────────────────────────────

    async def get_profit_breakdown(self, period: str) -> dict:
        key = make_cache_key(self.tenant_slug, "analytics:profit", period)
        hit = await cache_get(key)
        if hit is not None:
            return hit

        days = self._period_to_days(period)
        cutoff = datetime.utcnow() - timedelta(days=days)
        from app.models.remaining_models import SalesAnalytic

        r = (await self.db.execute(
            select(
                func.sum(SalesAnalytic.gross_revenue).label("gross"),
                func.sum(SalesAnalytic.cogs).label("cogs"),
                func.sum(SalesAnalytic.platform_fees).label("fees"),
                func.sum(SalesAnalytic.ad_spend).label("ads"),
                func.sum(SalesAnalytic.refunds).label("refunds"),
                func.sum(SalesAnalytic.net_profit).label("net"),
            ).where(SalesAnalytic.time >= cutoff)
        )).one()

        gross = float(r.gross or 0)
        result = {
            "gross_revenue": gross,
            "cogs": float(r.cogs or 0),
            "platform_fees": float(r.fees or 0),
            "ad_spend": float(r.ads or 0),
            "refunds": float(r.refunds or 0),
            "net_profit": float(r.net or 0),
            "margin_percent": round(float(r.net or 0) / gross * 100, 1) if gross else 0,
        }
        await cache_set(key, result, ttl=300)
        return result

    # ── By product ─────────────────────────────────────────────────────

    async def get_by_product(self, period: str, limit: int, sort_by: str) -> list:
        key = make_cache_key(self.tenant_slug, "analytics:by_product", period, sort_by, limit)
        hit = await cache_get(key)
        if hit is not None:
            return hit

        days = self._period_to_days(period)
        cutoff = datetime.utcnow() - timedelta(days=days)
        from app.models.remaining_models import SalesAnalytic
        from app.models.product import Product

        sort_expr = {
            "revenue": func.sum(SalesAnalytic.gross_revenue),
            "profit": func.sum(SalesAnalytic.net_profit),
            "units": func.sum(SalesAnalytic.units_sold),
        }.get(sort_by, func.sum(SalesAnalytic.gross_revenue))

        rows = (await self.db.execute(
            select(
                SalesAnalytic.product_id,
                Product.title,
                Product.marketplace,
                func.sum(SalesAnalytic.gross_revenue).label("revenue"),
                func.sum(SalesAnalytic.net_profit).label("profit"),
                func.sum(SalesAnalytic.units_sold).label("units"),
                func.sum(SalesAnalytic.ad_spend).label("ad_spend"),
            )
            .join(Product, SalesAnalytic.product_id == Product.id, isouter=True)
            .where(SalesAnalytic.time >= cutoff)
            .group_by(SalesAnalytic.product_id, Product.title, Product.marketplace)
            .order_by(desc(sort_expr))
            .limit(limit)
        )).all()

        result = [
            {
                "product_id": str(r.product_id),
                "title": r.title or "Unknown",
                "marketplace": r.marketplace,
                "revenue": float(r.revenue or 0),
                "profit": float(r.profit or 0),
                "units": int(r.units or 0),
                "ad_spend": float(r.ad_spend or 0),
            }
            for r in rows
        ]
        await cache_set(key, result, ttl=300)
        return result

    # ── By platform ────────────────────────────────────────────────────

    async def get_by_platform(self, period: str) -> list:
        key = make_cache_key(self.tenant_slug, "analytics:by_platform", period)
        hit = await cache_get(key)
        if hit is not None:
            return hit

        days = self._period_to_days(period)
        cutoff = datetime.utcnow() - timedelta(days=days)
        from app.models.remaining_models import SalesAnalytic

        rows = (await self.db.execute(
            select(
                SalesAnalytic.marketplace,
                func.sum(SalesAnalytic.gross_revenue).label("revenue"),
                func.sum(SalesAnalytic.net_profit).label("profit"),
                func.sum(SalesAnalytic.units_sold).label("units"),
            )
            .where(SalesAnalytic.time >= cutoff)
            .group_by(SalesAnalytic.marketplace)
            .order_by(desc(func.sum(SalesAnalytic.gross_revenue)))
        )).all()

        result = [
            {"marketplace": r.marketplace, "revenue": float(r.revenue or 0),
             "profit": float(r.profit or 0), "units": int(r.units or 0)}
            for r in rows
        ]
        await cache_set(key, result, ttl=300)
        return result

    # ── AI / CEO helpers (heavy — cache 1 h) ──────────────────────────

    async def get_daily_recommendations(self, tenant_id: str) -> list:
        key = make_cache_key(self.tenant_slug, "analytics:recommendations")
        hit = await cache_get(key)
        if hit is not None:
            return hit
        result: list = []  # filled by AI service in production
        await cache_set(key, result, ttl=3600)
        return result

    async def get_executive_summary(self, tenant_id: str, period: str) -> dict:
        key = make_cache_key(self.tenant_slug, "analytics:exec_summary", period)
        hit = await cache_get(key)
        if hit is not None:
            return hit

        overview = await self.get_overview(period)
        result = {
            "period": period,
            "headline": f"Revenue ${overview['revenue']:,.0f} ({overview['revenue_change']:+.1f}%)",
            "profit_margin": overview.get("roi", 0),
            "top_insight": "Strong growth driven by top marketplace",
            "overview": overview,
        }
        await cache_set(key, result, ttl=900)
        return result

    async def simulate(self, tenant_id: str, scenario_type: str, parameters: dict, forecast_months: int) -> dict:
        """Simulations are always freshly computed — not cached."""
        return {
            "scenario_type": scenario_type,
            "forecast_months": forecast_months,
            "projected_revenue": [0] * forecast_months,
            "projected_profit": [0] * forecast_months,
            "assumptions": parameters,
        }
