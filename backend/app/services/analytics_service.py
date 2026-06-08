"""Analytics aggregation service for dashboards and reporting."""
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc


class AnalyticsService:
    def __init__(self, db: AsyncSession, tenant_slug: str):
        self.db = db
        self.tenant_slug = tenant_slug

    async def get_overview(self, period: str, marketplace: Optional[str] = None) -> dict:
        days = self._period_to_days(period)
        cutoff = datetime.utcnow() - timedelta(days=days)
        prev_cutoff = cutoff - timedelta(days=days)

        from app.models.remaining_models import SalesAnalytic
        q = select(
            func.sum(SalesAnalytic.gross_revenue).label("revenue"),
            func.sum(SalesAnalytic.net_profit).label("profit"),
            func.sum(SalesAnalytic.units_sold).label("units"),
            func.sum(SalesAnalytic.orders).label("orders"),
            func.sum(SalesAnalytic.ad_spend).label("ad_spend"),
        ).where(SalesAnalytic.time >= cutoff)
        if marketplace:
            q = q.where(SalesAnalytic.marketplace == marketplace)
        result = await self.db.execute(q)
        current = result.one()

        prev_q = select(
            func.sum(SalesAnalytic.gross_revenue).label("revenue"),
            func.sum(SalesAnalytic.net_profit).label("profit"),
            func.sum(SalesAnalytic.units_sold).label("units"),
            func.sum(SalesAnalytic.orders).label("orders"),
            func.sum(SalesAnalytic.ad_spend).label("ad_spend"),
        ).where(SalesAnalytic.time >= prev_cutoff, SalesAnalytic.time < cutoff)
        if marketplace:
            prev_q = prev_q.where(SalesAnalytic.marketplace == marketplace)
        prev_result = await self.db.execute(prev_q)
        prev = prev_result.one()

        def pct_change(curr, prev_val):
            if not prev_val or prev_val == 0:
                return 0
            return round((curr - prev_val) / prev_val * 100, 1)

        revenue = float(current.revenue or 0)
        prev_revenue = float(prev.revenue or 0)
        profit = float(current.profit or 0)
        ad_spend = float(current.ad_spend or 0)
        units = int(current.units or 0)

        return {
            "period": period,
            "revenue": revenue,
            "revenue_change": pct_change(revenue, prev_revenue),
            "profit": profit,
            "profit_change": pct_change(profit, float(prev.profit or 0)),
            "units_sold": units,
            "orders": int(current.orders or 0),
            "ad_spend": ad_spend,
            "acos": round(ad_spend / revenue * 100, 1) if revenue > 0 else 0,
            "tacos": round(ad_spend / revenue * 100, 1) if revenue > 0 else 0,
            "roi": round(profit / max(revenue - profit, 1) * 100, 1) if revenue > 0 else 0,
        }

    async def get_revenue_series(self, period: str, group_by: str, marketplace: Optional[str]) -> list:
        days = self._period_to_days(period)
        cutoff = datetime.utcnow() - timedelta(days=days)
        from app.models.remaining_models import SalesAnalytic
        from sqlalchemy import func

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
        result = await self.db.execute(q)
        return [{"date": str(r.date), "revenue": float(r.revenue or 0),
                 "profit": float(r.profit or 0), "ad_spend": float(r.ad_spend or 0),
                 "units": int(r.units or 0)} for r in result.all()]

    async def get_profit_breakdown(self, period: str) -> dict:
        days = self._period_to_days(period)
        cutoff = datetime.utcnow() - timedelta(days=days)
        from app.models.remaining_models import SalesAnalytic
        result = await self.db.execute(
            select(
                func.sum(SalesAnalytic.gross_revenue).label("gross"),
                func.sum(SalesAnalytic.cogs).label("cogs"),
                func.sum(SalesAnalytic.platform_fees).label("fees"),
                func.sum(SalesAnalytic.ad_spend).label("ads"),
                func.sum(SalesAnalytic.refunds).label("refunds"),
                func.sum(SalesAnalytic.net_profit).label("net"),
            ).where(SalesAnalytic.time >= cutoff)
        )
        r = result.one()
        gross = float(r.gross or 0)
        return {
            "gross_revenue": gross,
            "cogs": float(r.cogs or 0),
            "platform_fees": float(r.fees or 0),
            "ad_spend": float(r.ads or 0),
            "refunds": float(r.refunds or 0),
            "net_profit": float(r.net or 0),
            "margin_percent": round(float(r.net or 0) / gross * 100, 1) if gross else 0,
        }

    async def get_by_product(self, period: str, limit: int, sort_by: str) -> list:
        days = self._period_to_days(period)
        cutoff = datetime.utcnow() - timedelta(days=days)
        from app.models.remaining_models import SalesAnalytic
        from app.models.product import Product
        sort_col = {"revenue": func.sum(SalesAnalytic.gross_revenue),
                    "profit": func.sum(SalesAnalytic.net_profit),
                    "units": func.sum(SalesAnalytic.units_sold)}.get(sort_by, func.sum(SalesAnalytic.gross_revenue))
        result = await self.db.execute(
            select(SalesAnalytic.product_id, func.sum(SalesAnalytic.gross_revenue).label("revenue"),
                   func.sum(SalesAnalytic.net_profit).label("profit"),
                   func.sum(SalesAnalytic.units_sold).label("units"))
            .where(SalesAnalytic.time >= cutoff)
            .group_by(SalesAnalytic.product_id)
            .order_by(desc(sort_col))
            .limit(limit)
        )
        return [{"product_id": str(r.product_id), "revenue": float(r.revenue or 0),
                 "profit": float(r.profit or 0), "units": int(r.units or 0)} for r in result.all()]

    async def get_by_platform(self, period: str) -> list:
        days = self._period_to_days(period)
        cutoff = datetime.utcnow() - timedelta(days=days)
        from app.models.remaining_models import SalesAnalytic
        result = await self.db.execute(
            select(SalesAnalytic.marketplace,
                   func.sum(SalesAnalytic.gross_revenue).label("revenue"),
                   func.sum(SalesAnalytic.net_profit).label("profit"),
                   func.sum(SalesAnalytic.orders).label("orders"))
            .where(SalesAnalytic.time >= cutoff)
            .group_by(SalesAnalytic.marketplace)
            .order_by(desc(func.sum(SalesAnalytic.gross_revenue)))
        )
        return [{"marketplace": r.marketplace, "revenue": float(r.revenue or 0),
                 "profit": float(r.profit or 0), "orders": int(r.orders or 0)} for r in result.all()]

    def _period_to_days(self, period: str) -> int:
        return {"7d": 7, "30d": 30, "90d": 90, "1y": 365}.get(period, 30)
