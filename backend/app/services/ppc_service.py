"""PPC campaign intelligence and optimization service."""
import json
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.core.config import settings

def _get_anthropic():
    from anthropic import AsyncAnthropic
    return AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY or "placeholder")

from app.core.ai_utils import ai_available as _ai_available

PPC_SYSTEM = """You are SellerVision AI's PPC Optimization Engine.
Analyze advertising campaign data and provide precise, actionable optimization recommendations.
Focus on improving ROAS, reducing ACoS, and finding keyword opportunities.
Be specific with bid adjustments, budget changes, and keyword actions."""


class PPCService:
    def __init__(self, db: AsyncSession = None, tenant_slug: str = None):
        self.db = db
        self.tenant_slug = tenant_slug

    async def list_campaigns(self, marketplace=None, status=None, high_acos_only=False):
        from app.models.remaining_models import PPCCampaign
        q = select(PPCCampaign)
        if marketplace:
            q = q.where(PPCCampaign.marketplace == marketplace)
        if status:
            q = q.where(PPCCampaign.status == status)
        if high_acos_only:
            q = q.where(PPCCampaign.acos > 0.25)
        result = await self.db.execute(q.order_by(desc(PPCCampaign.revenue)))
        return result.scalars().all()

    async def get_performance_summary(self, tenant_id: str, days: int = 30) -> dict:
        from app.models.remaining_models import PPCCampaign
        from sqlalchemy import func
        result = await self.db.execute(
            select(
                func.sum(PPCCampaign.revenue).label("revenue"),
                func.sum(PPCCampaign.spend_today).label("spend"),
                func.sum(PPCCampaign.impressions).label("impressions"),
                func.sum(PPCCampaign.clicks).label("clicks"),
                func.sum(PPCCampaign.orders).label("orders"),
            )
        )
        r = result.one()
        spend = float(r.spend or 0)
        revenue = float(r.revenue or 0)
        clicks = int(r.clicks or 0)
        return {
            "total_spend": spend,
            "total_revenue": revenue,
            "total_orders": int(r.orders or 0),
            "total_clicks": clicks,
            "total_impressions": int(r.impressions or 0),
            "acos": round(spend / revenue * 100, 2) if revenue > 0 else 0,
            "roas": round(revenue / spend, 2) if spend > 0 else 0,
            "ctr": round(clicks / int(r.impressions or 1) * 100, 3),
            "cvr": round(int(r.orders or 0) / clicks * 100, 2) if clicks > 0 else 0,
            "period_days": days,
        }

    async def get_ai_recommendations(self, tenant_id: str, optimization_goal: str) -> dict:
        perf = await self.get_performance_summary(tenant_id, 30)
        if not _ai_available():
            return {
                "overall_assessment": f"Demo mode â€” ACoS at {perf['acos']:.1f}%, {optimization_goal} optimization available with real API key.",
                "priority_actions": [
                    {"action": "Pause keyword 'generic widget'", "type": "pause", "target": "Campaign A", "current_value": "ACoS 68%", "recommended_value": "paused", "expected_impact": "-$120/mo waste", "urgency": "high"},
                    {"action": "Increase bid on 'premium organizer'", "type": "bid_increase", "target": "Campaign B", "current_value": "$0.85", "recommended_value": "$1.10", "expected_impact": "+$340/mo revenue", "urgency": "medium"},
                    {"action": "Add negative: 'cheap'", "type": "negate", "target": "All campaigns", "current_value": "none", "recommended_value": "negative exact", "expected_impact": "-$80/mo waste", "urgency": "medium"},
                ],
                "budget_recommendations": {"total_budget_change_percent": 12.0, "reasoning": "Reallocate from poor performers to top ROAS campaigns"},
                "keyword_harvesting": [{"search_term": "bamboo storage box", "suggested_match_type": "phrase", "estimated_volume": 18000}],
                "negative_keywords": [{"keyword": "diy", "reason": "Non-commercial intent"}, {"keyword": "how to", "reason": "Informational"}],
                "estimated_acos_improvement": 4.2,
                "estimated_roas_improvement": 0.8,
                "mode": "demo",
            }
        prompt = f"""Analyze these PPC performance metrics and provide specific optimization actions:

Performance Data:
- Total Spend: ${perf['total_spend']:.2f}
- Total Revenue: ${perf['total_revenue']:.2f}
- ACoS: {perf['acos']:.1f}%
- ROAS: {perf['roas']:.2f}x
- CTR: {perf['ctr']:.2f}%
- CVR: {perf['cvr']:.2f}%

Optimization Goal: {optimization_goal}

Return JSON: {{
  "overall_assessment": "string",
  "priority_actions": [
    {{
      "action": "string",
      "type": "bid_increase|bid_decrease|pause|negate|harvest|budget_change",
      "target": "campaign/keyword name",
      "current_value": "string",
      "recommended_value": "string",
      "expected_impact": "string",
      "urgency": "critical|high|medium|low"
    }}
  ],
  "budget_recommendations": {{
    "total_budget_change_percent": float,
    "reasoning": "string"
  }},
  "keyword_harvesting": [{{"search_term": "...", "suggested_match_type": "...", "estimated_volume": integer}}],
  "negative_keywords": [{{"keyword": "...", "reason": "..."}}],
  "estimated_acos_improvement": float,
  "estimated_roas_improvement": float
}}"""

        msg = await _get_anthropic().messages.create(
            model=settings.ANTHROPIC_MODEL, max_tokens=3000,
            system=PPC_SYSTEM, messages=[{"role": "user", "content": prompt}]
        )
        return json.loads(msg.content[0].text)

    async def optimize_campaign(self, campaign_id: str) -> dict:
        from app.models.remaining_models import PPCCampaign
        result = await self.db.execute(select(PPCCampaign).where(PPCCampaign.id == campaign_id))
        campaign = result.scalar_one_or_none()
        if not campaign:
            return {"error": "Campaign not found"}

        if not _ai_available():
            return {"recommendation": "Demo mode", "bid_adjustments": [], "budget_change": 0, "mode": "demo"}
        prompt = f"""Optimize this specific PPC campaign:
Name: {campaign.name}
Type: {campaign.type}
Status: {campaign.status}
Daily Budget: ${float(campaign.daily_budget or 0):.2f}
ACoS: {float(campaign.acos or 0) * 100:.1f}%
ROAS: {float(campaign.roas or 0):.2f}x
Impressions: {campaign.impressions:,}
Clicks: {campaign.clicks:,}
Orders: {campaign.orders:,}

Return JSON with specific bid adjustments and budget changes."""

        msg = await _get_anthropic().messages.create(
            model=settings.ANTHROPIC_MODEL, max_tokens=1500,
            system=PPC_SYSTEM, messages=[{"role": "user", "content": prompt}]
        )
        recs = json.loads(msg.content[0].text)
        campaign.ai_recommendations = recs
        await self.db.commit()
        return recs

    async def get_harvest_suggestions(self, campaign_id: Optional[str]) -> list:
        if not _ai_available():
            return [
                {"search_term": "bamboo kitchen organizer", "suggested_match_type": "exact", "estimated_monthly_volume": 28000, "potential_orders_monthly": 140},
                {"search_term": "drawer divider set", "suggested_match_type": "phrase", "estimated_monthly_volume": 15000, "potential_orders_monthly": 90},
                {"search_term": "pantry storage bins", "suggested_match_type": "exact", "estimated_monthly_volume": 22000, "potential_orders_monthly": 110},
            ]
        prompt = """Suggest 15 profitable search terms to harvest as exact/phrase match keywords.
Include: search_term, suggested_match_type, estimated_monthly_volume, potential_orders_monthly.
Return JSON array."""
        msg = await _get_anthropic().messages.create(
            model=settings.ANTHROPIC_MODEL, max_tokens=1000,
            system=PPC_SYSTEM, messages=[{"role": "user", "content": prompt}]
        )
        return json.loads(msg.content[0].text)

    async def get_negative_suggestions(self) -> list:
        if not _ai_available():
            return [
                {"keyword": "free", "match_type": "broad", "reason": "Non-buyers", "estimated_monthly_savings": 45},
                {"keyword": "how to make", "match_type": "phrase", "reason": "DIY intent", "estimated_monthly_savings": 32},
                {"keyword": "cheap", "match_type": "broad", "reason": "Price-sensitive, low CVR", "estimated_monthly_savings": 28},
                {"keyword": "used", "match_type": "exact", "reason": "Not selling used items", "estimated_monthly_savings": 22},
                {"keyword": "wholesale", "match_type": "exact", "reason": "B2B intent, wrong audience", "estimated_monthly_savings": 18},
            ]
        prompt = """Suggest 20 negative keywords to add to Amazon PPC campaigns to reduce wasted spend.
Include: keyword, match_type, reason, estimated_monthly_savings.
Return JSON array."""
        msg = await _get_anthropic().messages.create(
            model=settings.ANTHROPIC_MODEL, max_tokens=1000,
            system=PPC_SYSTEM, messages=[{"role": "user", "content": prompt}]
        )
        return json.loads(msg.content[0].text)

    async def run_optimization_cycle(self, tenant_slug: str) -> None:
        """Celery task: auto-optimize all campaigns."""
        from app.models.remaining_models import PPCCampaign
        result = await self.db.execute(
            select(PPCCampaign).where(PPCCampaign.status == "enabled")
        )
        campaigns = result.scalars().all()
        for campaign in campaigns:
            if campaign.acos and float(campaign.acos) > 0.30:
                await self.optimize_campaign(str(campaign.id))
