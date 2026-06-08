"""Module 14: Trend Discovery & Prediction Engine."""
import json
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.cache import cached

def _get_anthropic():
    from anthropic import AsyncAnthropic
    return AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY or "placeholder")

from app.core.ai_utils import ai_available as _ai_available

TREND_SYSTEM = """You are SellerVision AI's Trend Intelligence Engine.
You monitor and predict e-commerce trends across all platforms.
Provide accurate, commercially actionable trend analysis with realistic scores.
Base analysis on real product trend patterns."""


class TrendService:
    def __init__(self, db: AsyncSession = None, tenant_slug: str = None):
        self.db = db
        self.tenant_slug = tenant_slug

    async def list_trends(self, category=None, source=None, min_score=0, limit=20):
        from app.models.remaining_models import Trend
        from sqlalchemy import select, desc
        q = select(Trend).where(Trend.trend_score >= min_score).order_by(desc(Trend.trend_score)).limit(limit)
        if category:
            q = q.where(Trend.category.ilike(f"%{category}%"))
        if source:
            q = q.where(Trend.source == source)
        result = await self.db.execute(q)
        return result.scalars().all()

    @cached(ttl=1800, key_prefix="trend_detect")
    async def detect_trends(self, category: str, sources: List[str], lookback_days: int = 30) -> dict:
        if not _ai_available():
            return {
                "detected_at": "2026-06-05T00:00:00",
                "category": category or "general",
                "trends": [
                    {"topic": "Eco-friendly packaging", "source": sources[0] if sources else "google", "trend_score": 84.0, "momentum_score": 78.0, "viral_score": 62.0, "lifespan_prediction": "sustained", "peak_date_estimate": "2026-09", "related_products": ["bamboo containers", "recycled paper bags"], "commercial_opportunity": "high", "entry_window": "now", "reasoning": "Growing consumer demand for sustainable packaging"},
                    {"topic": "Smart home accessories", "source": sources[0] if sources else "google", "trend_score": 76.0, "momentum_score": 71.0, "viral_score": 58.0, "lifespan_prediction": "evergreen", "peak_date_estimate": "2026-12", "related_products": ["smart plugs", "LED controllers"], "commercial_opportunity": "high", "entry_window": "now", "reasoning": "Consistent category growth driven by home automation adoption"},
                    {"topic": "Portable fitness gear", "source": sources[0] if sources else "tiktok", "trend_score": 69.0, "momentum_score": 82.0, "viral_score": 74.0, "lifespan_prediction": "seasonal", "peak_date_estimate": "2026-08", "related_products": ["resistance bands", "foldable mats"], "commercial_opportunity": "medium", "entry_window": "now", "reasoning": "Summer fitness trend peaking on TikTok"},
                ],
                "top_opportunity": "Eco-friendly packaging",
                "recommended_action": "Source bamboo or recycled-material products immediately to capitalize on Q3 demand",
                "mode": "demo",
            }
        sources_str = ", ".join(sources)
        prompt = f"""Detect emerging e-commerce trends for category: {category or 'all'}
Data sources: {sources_str}
Lookback: {lookback_days} days

Return JSON: {{
  "detected_at": "ISO timestamp",
  "category": "{category or 'general'}",
  "trends": [
    {{
      "topic": "string",
      "source": "{sources[0]}",
      "trend_score": float (0-100),
      "momentum_score": float (0-100),
      "viral_score": float (0-100),
      "lifespan_prediction": "short_lived/seasonal/sustained/evergreen",
      "peak_date_estimate": "YYYY-MM",
      "related_products": ["product1", "product2"],
      "commercial_opportunity": "high/medium/low",
      "entry_window": "now/3_months/6_months",
      "reasoning": "string"
    }}
  ],
  "top_opportunity": "string",
  "recommended_action": "string"
}}"""
        msg = await _get_anthropic().messages.create(
            model=settings.ANTHROPIC_MODEL, max_tokens=3000,
            system=TREND_SYSTEM, messages=[{"role": "user", "content": prompt}]
        )
        data = json.loads(msg.content[0].text)

        # Persist detected trends
        if self.db:
            from app.models.remaining_models import Trend
            for t in data.get("trends", []):
                trend = Trend(
                    topic=t["topic"],
                    source=t.get("source", sources[0]),
                    category=category or "general",
                    trend_score=t.get("trend_score", 0),
                    momentum_score=t.get("momentum_score", 0),
                    viral_score=t.get("viral_score", 0),
                    lifespan_prediction=t.get("lifespan_prediction"),
                    related_products=t.get("related_products", []),
                    ai_analysis=t,
                )
                self.db.add(trend)
            await self.db.commit()
        return data

    async def get_emerging(self, limit: int = 10) -> list:
        from datetime import datetime, timedelta
        from app.models.remaining_models import Trend
        from sqlalchemy import select, desc
        cutoff = datetime.utcnow() - timedelta(hours=48)
        result = await self.db.execute(
            select(Trend).where(Trend.detected_at >= cutoff)
            .order_by(desc(Trend.trend_score)).limit(limit)
        )
        return result.scalars().all()

    @cached(ttl=900, key_prefix="viral_products")
    async def get_viral_products(self, marketplace: str, limit: int) -> list:
        if not _ai_available():
            return [
                {"product_name": "Stanley Quencher Tumbler", "category": "drinkware", "viral_score": 96, "estimated_daily_views": 2400000, "growth_rate_percent": 340, "commercial_opportunity": "high", "best_selling_price_range": "$35-55", "key_selling_points": ["Keeps drinks cold 24h", "Viral TikTok trend", "Limited colors drive FOMO"]},
                {"product_name": "Air Fryer Silicone Liner", "category": "kitchen", "viral_score": 84, "estimated_daily_views": 980000, "growth_rate_percent": 128, "commercial_opportunity": "high", "best_selling_price_range": "$12-22", "key_selling_points": ["Easy cleanup", "Fits all sizes", "Reusable eco-friendly"]},
                {"product_name": "Portable Blender", "category": "fitness", "viral_score": 79, "estimated_daily_views": 720000, "growth_rate_percent": 95, "commercial_opportunity": "medium", "best_selling_price_range": "$25-45", "key_selling_points": ["USB rechargeable", "On-the-go smoothies", "BPA-free"]},
            ][:limit]
        prompt = f"""List the top {limit} products going viral on {marketplace} right now.
For each: product_name, category, viral_score, estimated_daily_views, growth_rate_percent,
commercial_opportunity, best_selling_price_range, key_selling_points.
Return as JSON array."""
        msg = await _get_anthropic().messages.create(
            model=settings.ANTHROPIC_MODEL, max_tokens=2000,
            system=TREND_SYSTEM, messages=[{"role": "user", "content": prompt}]
        )
        return json.loads(msg.content[0].text)

    async def predict_trend(self, trend_id: str) -> dict:
        if self.db:
            from app.models.remaining_models import Trend
            from sqlalchemy import select
            result = await self.db.execute(select(Trend).where(Trend.id == trend_id))
            trend = result.scalar_one_or_none()
            if not trend:
                from fastapi import HTTPException
                raise HTTPException(404, "Trend not found")
            topic = trend.topic
        else:
            topic = trend_id

        if not _ai_available():
            return {
                "trend": topic, "current_phase": "growing",
                "months_to_peak": 4, "months_total_lifespan": 18,
                "peak_revenue_potential_monthly": 85000.0, "competition_at_peak": "medium",
                "optimal_entry_now": True, "optimal_exit_date": "2027-03",
                "risk_factors": ["Increasing competition", "Seasonal dependency"],
                "success_factors": ["Early mover advantage", "Strong brand differentiation"],
                "similar_past_trends": ["Fidget spinners (2017)", "Instant Pots (2019)"],
                "confidence_score": 0.71, "recommendation": "enter_now", "mode": "demo",
            }
        prompt = f"""Predict the full lifecycle of this trend: "{topic}"

Return JSON: {{
  "trend": "{topic}",
  "current_phase": "emerging/growing/peak/declining",
  "months_to_peak": integer,
  "months_total_lifespan": integer,
  "peak_revenue_potential_monthly": float,
  "competition_at_peak": "low/medium/high/very_high",
  "optimal_entry_now": boolean,
  "optimal_exit_date": "YYYY-MM",
  "risk_factors": ["..."],
  "success_factors": ["..."],
  "similar_past_trends": ["..."],
  "confidence_score": float,
  "recommendation": "enter_now/wait/avoid"
}}"""
        msg = await _get_anthropic().messages.create(
            model=settings.ANTHROPIC_MODEL, max_tokens=1500,
            system=TREND_SYSTEM, messages=[{"role": "user", "content": prompt}]
        )
        return json.loads(msg.content[0].text)

    async def run_full_trend_scan(self) -> None:
        """Called by Celery beat â€” scan all major categories."""
        categories = ["health_beauty", "kitchen_home", "pet_supplies", "sports_outdoors",
                      "electronics", "clothing", "toys_games", "office_supplies"]
        sources = ["google", "tiktok", "reddit", "pinterest", "amazon"]
        import asyncio
        tasks = [self.detect_trends(cat, sources, 14) for cat in categories]
        await asyncio.gather(*tasks, return_exceptions=True)
