"""
Module 18: AI CEO Dashboard -- provides executive decisions, not just charts.
Module 19: E-Commerce Digital Twin -- simulate business scenarios.
"""
import json
from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.config import settings


def _get_anthropic():
    from anthropic import AsyncAnthropic
    return AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY or "placeholder")


CEO_SYSTEM_PROMPT = """You are the AI CEO of an e-commerce business. You have access to all business data.
Your job is NOT to show charts -- your job is to make DECISIONS and give COMMANDS.
Every recommendation must be:
1. Specific (exact product, amount, date)
2. Actionable (one clear next step)
3. Prioritized (highest ROI first)
4. Reasoned (brief why)

Format as executive action items, not analysis."""

DIGITAL_TWIN_PROMPT = """You are SellerVision AI's Digital Twin Engine.
You simulate e-commerce business scenarios with financial precision.
Given a change scenario, project outcomes over the specified period.
Always include: revenue impact, profit impact, cash flow, inventory implications,
market share change, risk assessment, confidence interval."""


from app.core.ai_utils import ai_available as _ai_available


_DEMO_RECOMMENDATIONS = [
    {"action": "Reorder 500 units of Widget A", "product_or_area": "Widget A", "expected_impact": "+$8,400 avoided lost revenue", "urgency": "critical", "effort": 5, "reasoning": "Stockout predicted in 11 days; lead time is 28 days."},
    {"action": "Increase price on Gadget Pro by 7%", "product_or_area": "Gadget Pro", "expected_impact": "+$1,200/mo profit", "urgency": "high", "effort": 2, "reasoning": "Competitors priced 12% higher; buy box secured at current price."},
    {"action": "Pause 3 high-ACoS keywords", "product_or_area": "PPC Campaign #4", "expected_impact": "-$340/mo wasted spend", "urgency": "high", "effort": 10, "reasoning": "ACoS >45% for 14 days with no conversions."},
    {"action": "Expand Gadget X to Walmart Marketplace", "product_or_area": "Gadget X", "expected_impact": "+$3,200/mo revenue", "urgency": "medium", "effort": 60, "reasoning": "Walmart demand score 78/100; low competition detected."},
    {"action": "Optimize 7 listings below SEO score 70", "product_or_area": "Listings", "expected_impact": "+15-25% organic traffic", "urgency": "medium", "effort": 120, "reasoning": "Missing target keywords in titles; avg score 52/100."},
    {"action": "Request quotes from 2 backup suppliers", "product_or_area": "Supply Chain", "expected_impact": "Risk mitigation", "urgency": "medium", "effort": 30, "reasoning": "Primary supplier lead time increased to 35 days."},
    {"action": "Run flash sale on slow-moving SKU #7", "product_or_area": "SKU-007", "expected_impact": "+$600 inventory recovery", "urgency": "low", "effort": 15, "reasoning": "90-day sell-through rate below threshold."},
    {"action": "Enable Subscribe & Save on top 5 products", "product_or_area": "Amazon listings", "expected_impact": "+8% repeat revenue", "urgency": "low", "effort": 20, "reasoning": "Subscription eligibility confirmed; competitors using it."},
    {"action": "Add 3 new A+ content images to Widget B", "product_or_area": "Widget B", "expected_impact": "+5-12% conversion rate", "urgency": "low", "effort": 45, "reasoning": "Competitor A+ content is outperforming by 2 conversion points."},
    {"action": "File reimbursement claim for 23 lost units", "product_or_area": "Amazon FBA", "expected_impact": "+$380 recovered", "urgency": "low", "effort": 10, "reasoning": "Inventory discrepancy identified in last reconciliation."},
]


class CEODashboardService:

    def __init__(self, db: Optional[AsyncSession] = None):
        self.db = db

    async def get_daily_recommendations(self, tenant_id: str) -> dict:
        """Generate AI CEO's daily action plan."""
        business_data = await self._fetch_business_snapshot(tenant_id)

        if not _ai_available():
            return {
                "date": datetime.now().isoformat(),
                "recommendations": _DEMO_RECOMMENDATIONS,
                "business_score": business_data.get("overall_health_score", 72),
                "mode": "demo",
            }

        prompt = f"""Based on this business snapshot, generate today's top 10 action items:

Business Data:
{json.dumps(business_data, indent=2, default=str)}

Today's Date: {datetime.now().strftime('%Y-%m-%d')}

Generate 10 specific action items ranked by expected ROI impact.
For each action include:
- action: specific instruction
- product_or_area: what it applies to
- expected_impact: $ or % improvement
- urgency: critical/high/medium/low
- effort: minutes to complete
- reasoning: one sentence why"""

        message = await _get_anthropic().messages.create(
            model=settings.ANTHROPIC_MODEL,
            max_tokens=3000,
            system=CEO_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}]
        )

        try:
            actions = json.loads(message.content[0].text)
        except json.JSONDecodeError:
            actions = {"actions": [], "raw": message.content[0].text}

        return {
            "date": datetime.now().isoformat(),
            "recommendations": actions,
            "business_score": business_data.get("overall_health_score", 0),
        }

    async def get_executive_summary(self, tenant_id: str, period: str = "week") -> dict:
        """Weekly/monthly executive summary with forward projections."""
        business_data = await self._fetch_business_snapshot(tenant_id)

        if not _ai_available():
            return {
                "period": period,
                "summary": "Demo mode -- connect a real Anthropic API key to generate live executive summaries.",
                "generated_at": datetime.now().isoformat(),
                "mode": "demo",
            }

        prompt = f"""Generate an executive summary for period: {period}

Business Performance:
{json.dumps(business_data, indent=2, default=str)}

Include:
1. Performance vs last period
2. Top 3 wins
3. Top 3 problems requiring attention
4. Forward projection for next {period}
5. Strategic recommendations (1-3)
6. Risk alerts
7. Cash flow forecast"""

        message = await _get_anthropic().messages.create(
            model=settings.ANTHROPIC_MODEL,
            max_tokens=4000,
            system=CEO_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}]
        )
        return {"period": period, "summary": message.content[0].text, "generated_at": datetime.now().isoformat()}

    async def _fetch_business_snapshot(self, tenant_id: str) -> dict:
        """Aggregate key business metrics from the real DB for AI analysis."""
        from app.models.remaining_models import SalesAnalytic, PPCCampaign, Listing, Competitor, Trend
        from app.models.product import Product
        from app.models.inventory import Inventory

        # Fallback if no DB session
        if not self.db:
            return {
                "tenant_id": tenant_id,
                "overall_health_score": 72,
                "total_revenue_30d": 48500,
                "total_revenue_prev_30d": 42300,
                "total_profit_30d": 12800,
                "active_products": 23,
                "products_needing_reorder": 4,
                "products_at_risk_stockout": 2,
                "campaigns_high_acos": 3,
                "listings_below_score_70": 7,
                "new_competitor_threats": 2,
                "trending_opportunities": 5,
            }

        now = datetime.now(timezone.utc)
        cutoff_30d = now - timedelta(days=30)
        cutoff_60d = now - timedelta(days=60)
        stockout_threshold = (now + timedelta(days=14)).date()

        # --- Sales: current 30d vs prev 30d ---
        sales_q = await self.db.execute(
            select(
                func.sum(SalesAnalytic.gross_revenue).label("revenue"),
                func.sum(SalesAnalytic.net_profit).label("profit"),
                func.sum(SalesAnalytic.units_sold).label("units"),
                func.sum(SalesAnalytic.ad_spend).label("ad_spend"),
            ).where(SalesAnalytic.time >= cutoff_30d)
        )
        sales = sales_q.one()
        revenue_30d = float(sales.revenue or 0)
        profit_30d = float(sales.profit or 0)
        units_30d = int(sales.units or 0)
        ad_spend_30d = float(sales.ad_spend or 0)

        prev_q = await self.db.execute(
            select(func.sum(SalesAnalytic.gross_revenue).label("revenue"))
            .where(SalesAnalytic.time >= cutoff_60d, SalesAnalytic.time < cutoff_30d)
        )
        revenue_prev = float((prev_q.one()).revenue or 0)

        # --- Products ---
        active_products = await self.db.scalar(
            select(func.count()).select_from(Product).where(Product.is_own_product == True)
        ) or 0

        # --- Inventory alerts ---
        products_reorder = await self.db.scalar(
            select(func.count()).select_from(Inventory)
            .where(Inventory.quantity_on_hand <= Inventory.reorder_point)
        ) or 0

        products_stockout_risk = await self.db.scalar(
            select(func.count()).select_from(Inventory)
            .where(
                Inventory.stockout_date != None,
                Inventory.stockout_date <= stockout_threshold,
                Inventory.quantity_on_hand > 0,
            )
        ) or 0

        # --- PPC high ACoS ---
        high_acos = await self.db.scalar(
            select(func.count()).select_from(PPCCampaign)
            .where(PPCCampaign.acos > 0.25, PPCCampaign.status == "enabled")
        ) or 0

        # --- Listings below SEO score 70 ---
        weak_listings = await self.db.scalar(
            select(func.count()).select_from(Listing)
            .where(Listing.seo_score < 70, Listing.seo_score != None)
        ) or 0

        # --- Competitor threats ---
        competitor_threats = await self.db.scalar(
            select(func.count()).select_from(Competitor)
            .where(Competitor.threat_level == "high")
        ) or 0

        # --- Trending opportunities ---
        trending_opps = await self.db.scalar(
            select(func.count()).select_from(Trend)
            .where(Trend.trend_score >= 70)
        ) or 0

        # --- Compute composite health score (0-100) ---
        health = 100
        if revenue_30d > 0 and revenue_prev > 0:
            rev_growth = (revenue_30d - revenue_prev) / revenue_prev
            if rev_growth < -0.1:
                health -= 15
            elif rev_growth < 0:
                health -= 5
        acos_pct = (ad_spend_30d / revenue_30d * 100) if revenue_30d > 0 else 0
        if acos_pct > 30:
            health -= 10
        elif acos_pct > 20:
            health -= 5
        health -= min(products_stockout_risk * 5, 20)
        health -= min(high_acos * 3, 12)
        health -= min(weak_listings * 1, 10)
        health = max(0, min(100, health))

        return {
            "tenant_id": tenant_id,
            "overall_health_score": health,
            "total_revenue_30d": round(revenue_30d, 2),
            "total_revenue_prev_30d": round(revenue_prev, 2),
            "total_profit_30d": round(profit_30d, 2),
            "units_sold_30d": units_30d,
            "ad_spend_30d": round(ad_spend_30d, 2),
            "acos_pct": round(acos_pct, 1),
            "active_products": active_products,
            "products_needing_reorder": products_reorder,
            "products_at_risk_stockout": products_stockout_risk,
            "campaigns_high_acos": high_acos,
            "listings_below_score_70": weak_listings,
            "new_competitor_threats": competitor_threats,
            "trending_opportunities": trending_opps,
        }


class DigitalTwinService:

    def __init__(self, db: Optional[AsyncSession] = None):
        self.db = db

    async def simulate(
        self,
        tenant_id: str,
        scenario_type: str,
        parameters: dict,
        forecast_months: int = 6,
    ) -> dict:
        """Run what-if business simulation."""
        business_data = await self._get_business_baseline(tenant_id)

        scenario_descriptions = {
            "price_change": f"Change product price by {parameters.get('change_percent', 0)}%",
            "ppc_increase": f"Increase PPC budget by ${parameters.get('increase_amount', 0)}/day",
            "new_product": f"Launch new product: {parameters.get('product_name', 'Unknown')} at ${parameters.get('price', 0)}",
            "inventory_change": f"Change inventory level to {parameters.get('new_level', 0)} units",
        }

        scenario_description = scenario_descriptions.get(scenario_type, str(parameters))

        if not _ai_available():
            return {
                "tenant_id": tenant_id,
                "scenario_type": scenario_type,
                "parameters": parameters,
                "forecast_months": forecast_months,
                "simulation": {"raw_simulation": "Demo mode -- connect a real Anthropic API key to run Digital Twin simulations."},
                "generated_at": datetime.now().isoformat(),
                "mode": "demo",
            }

        prompt = f"""Simulate this business scenario for {forecast_months} months:

SCENARIO: {scenario_description}

CURRENT BUSINESS BASELINE:
{json.dumps(business_data, indent=2, default=str)}

PARAMETERS:
{json.dumps(parameters, indent=2)}

Return JSON with:
- scenario_summary: string
- months: array of {forecast_months} monthly projections, each with:
  - month: number
  - revenue: number
  - profit: number
  - cash_flow: number
  - units_sold: number
  - acos: number (if PPC scenario)
  - inventory_remaining: number
- total_6m_revenue: number
- total_6m_profit: number
- roi_percent: number
- break_even_month: number
- risk_assessment: string
- confidence_interval: {{low, mid, high}} revenue at 6m
- recommendation: go/pause/no_go
- key_assumptions: array of strings"""

        message = await _get_anthropic().messages.create(
            model=settings.ANTHROPIC_MODEL,
            max_tokens=4096,
            system=DIGITAL_TWIN_PROMPT,
            messages=[{"role": "user", "content": prompt}]
        )

        try:
            result = json.loads(message.content[0].text)
        except json.JSONDecodeError:
            result = {"raw_simulation": message.content[0].text}

        return {
            "tenant_id": tenant_id,
            "scenario_type": scenario_type,
            "parameters": parameters,
            "forecast_months": forecast_months,
            "simulation": result,
            "generated_at": datetime.now().isoformat(),
        }

    async def _get_business_baseline(self, tenant_id: str) -> dict:
        """Real DB baseline for Digital Twin simulations."""
        from app.models.remaining_models import SalesAnalytic
        from app.models.product import Product
        from app.models.inventory import Inventory

        if not self.db:
            return {
                "monthly_revenue": 16000,
                "monthly_profit": 4200,
                "monthly_units": 340,
                "current_acos": 0.22,
                "inventory_days": 45,
                "top_products": ["Widget A", "Gadget B"],
            }

        cutoff_30d = datetime.now(timezone.utc) - timedelta(days=30)

        # 30-day sales aggregation
        sales_q = await self.db.execute(
            select(
                func.sum(SalesAnalytic.gross_revenue).label("revenue"),
                func.sum(SalesAnalytic.net_profit).label("profit"),
                func.sum(SalesAnalytic.units_sold).label("units"),
                func.sum(SalesAnalytic.ad_spend).label("ad_spend"),
            ).where(SalesAnalytic.time >= cutoff_30d)
        )
        s = sales_q.one()
        revenue = float(s.revenue or 0)
        ad_spend = float(s.ad_spend or 0)

        # Top products by revenue
        top_q = await self.db.execute(
            select(Product.title, func.sum(SalesAnalytic.gross_revenue).label("rev"))
            .join(SalesAnalytic, SalesAnalytic.product_id == Product.id)
            .where(SalesAnalytic.time >= cutoff_30d)
            .group_by(Product.id, Product.title)
            .order_by(func.sum(SalesAnalytic.gross_revenue).desc())
            .limit(5)
        )
        top_products = [r.title for r in top_q.all()]

        # Average inventory days remaining
        inv_q = await self.db.execute(
            select(func.avg(
                func.extract("day", Inventory.stockout_date - func.current_date())
            )).where(Inventory.stockout_date != None)
        )
        avg_inv_days = float(inv_q.scalar() or 45)

        return {
            "monthly_revenue": round(revenue, 2),
            "monthly_profit": round(float(s.profit or 0), 2),
            "monthly_units": int(s.units or 0),
            "current_acos": round(ad_spend / revenue, 4) if revenue > 0 else 0,
            "inventory_days": round(avg_inv_days, 1),
            "top_products": top_products or ["Unknown"],
        }
