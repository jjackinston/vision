"""Competitor monitoring and analysis service."""
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.models.remaining_models import Competitor


class CompetitorService:
    def __init__(self, db: AsyncSession = None, tenant_slug: str = None):
        self.db = db
        self.tenant_slug = tenant_slug

    async def list_competitors(self, product_id=None, marketplace=None):
        q = select(Competitor)
        if product_id:
            q = q.where(Competitor.product_id == product_id)
        if marketplace:
            q = q.where(Competitor.marketplace == marketplace)
        result = await self.db.execute(q.order_by(desc(Competitor.monthly_revenue)))
        return result.scalars().all()

    async def track_competitor(self, asin: str, marketplace: str, product_id: Optional[str]) -> dict:
        if marketplace == "amazon":
            from app.integrations.amazon.sp_api import AmazonSPAPI
            api = AmazonSPAPI()
            catalog = await api.get_catalog_item(asin)
            pricing = await api.get_competitive_pricing(asin)
            title = catalog.get("summaries", [{}])[0].get("itemName", "Unknown")
            price = None
            try:
                price = pricing["payload"][0]["Product"]["CompetitivePricing"]["CompetitivePrices"][0]["Price"]["LandedPrice"]["Amount"]
            except (KeyError, IndexError):
                pass
        else:
            title = f"Competitor on {marketplace}"
            price = None

        existing = await self.db.execute(
            select(Competitor).where(Competitor.asin == asin, Competitor.marketplace == marketplace)
        )
        competitor = existing.scalar_one_or_none()
        if competitor:
            competitor.price = price
            competitor.title = title
        else:
            competitor = Competitor(
                asin=asin, marketplace=marketplace, title=title, price=price,
                product_id=product_id, threat_level="unknown",
            )
            self.db.add(competitor)
        await self.db.commit()
        await self.db.refresh(competitor)
        return {"id": str(competitor.id), "asin": asin, "title": title, "price": price}

    async def get_price_history(self, competitor_id: UUID, days: int) -> list:
        # In production: query timescale product_metrics table for this competitor's ASIN
        from datetime import datetime, timedelta
        return [
            {"date": (datetime.utcnow() - timedelta(days=i)).strftime("%Y-%m-%d"),
             "price": 29.99 - (i * 0.05)}
            for i in range(0, min(days, 30), 3)
        ]

    async def analyze_threat(self, competitor_id: UUID) -> dict:
        result = await self.db.execute(select(Competitor).where(Competitor.id == competitor_id))
        comp = result.scalar_one_or_none()
        if not comp:
            return {}
        return {
            "competitor": comp.title,
            "threat_level": comp.threat_level,
            "monthly_revenue": float(comp.monthly_revenue or 0),
            "strengths": comp.weakness_analysis.get("strengths", []),
            "weaknesses": comp.weakness_analysis.get("weaknesses", []),
            "recommended_counter_strategy": "Focus on quality differentiation and superior customer service",
        }

    async def get_market_overview(self, category: str, marketplace: str) -> dict:
        from app.services.ai_product_service import AIProductService
        ai_service = AIProductService()
        return await ai_service.analyze_saturation(category, marketplace)

    async def monitor_all(self) -> None:
        """Background: check for price/stock changes on all tracked competitors."""
        if not self.db:
            from app.core.database import AsyncSessionLocal
            async with AsyncSessionLocal() as db:
                await CompetitorService(db).monitor_all()
            return
        result = await self.db.execute(select(Competitor).limit(200))
        competitors = result.scalars().all()
        from app.integrations.amazon.sp_api import AmazonSPAPI
        api = AmazonSPAPI()
        for comp in competitors:
            if comp.asin:
                try:
                    pricing = await api.get_competitive_pricing(comp.asin)
                    # Update price if changed, emit notification if significant
                except Exception:
                    pass
