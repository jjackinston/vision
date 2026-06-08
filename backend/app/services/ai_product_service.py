"""
AI Product Service â€” Core intelligence engine for all product-related AI features.
Covers Modules 1-7, 10: Opportunity scoring, success prediction, saturation radar,
competitor weakness scanning, AI product creation, platform recommendations,
and launch simulation.
"""
import json
from typing import Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from app.core.config import settings
from app.core.cache import cached
from app.schemas.product import (
    ProductOpportunityScore, ProductSuccessPrediction,
    SaturationRadar, LaunchSimulatorInput, LaunchSimulatorResult,
)


def _get_anthropic():
    from anthropic import AsyncAnthropic
    return AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY or "placeholder")

from app.core.ai_utils import ai_available as _ai_available


def _get_openai():
    from openai import AsyncOpenAI
    return AsyncOpenAI(api_key=settings.OPENAI_API_KEY or "placeholder")


def _get_llm():
    from langchain_openai import ChatOpenAI
    return ChatOpenAI(model=settings.OPENAI_MODEL, api_key=settings.OPENAI_API_KEY or "placeholder")


OPPORTUNITY_SYSTEM_PROMPT = """You are SellerVision AI's Product Opportunity Engine.
You analyze e-commerce product data to generate precise opportunity scores.
Always return structured JSON with numerical scores (0-100) and actionable reasoning.
Base your analysis on: demand signals, competition density, margin potential,
trend trajectory, and barrier to entry."""

SUCCESS_PREDICTOR_PROMPT = """You are SellerVision AI's Product Success Predictor.
Given a product concept and market data, calculate the probability of success (0-100%).
Provide: success_probability, estimated_revenue_monthly, estimated_profit_monthly,
break_even_months, risk_factors (list), opportunities (list), recommendation (launch/wait/avoid),
and explainable_reasoning (paragraph). Be precise and data-driven."""

SATURATION_PROMPT = """You are SellerVision AI's Market Saturation Radar.
Analyze the provided market signals to forecast saturation at 3, 6, and 12 months.
Return: current_saturation_score, saturation_3m, saturation_6m, saturation_12m,
new_seller_velocity, review_velocity_trend, entry_risk_score, exit_risk_score,
heat_map_data (array of {segment, score}), recommendation."""

WEAKNESS_SCANNER_PROMPT = """You are SellerVision AI's Competitor Weakness Scanner.
Analyze competitor reviews, ratings, and listing data to identify:
- Product defects and quality issues
- Packaging complaints
- Missing features customers request
- Customer frustrations
- Service failures
For each weakness found, generate a specific product improvement opportunity.
Return structured JSON with: weaknesses[], opportunities[], differentiation_strategies[],
competitive_advantage_score (0-100)."""

PRODUCT_CREATOR_PROMPT = """You are SellerVision AI's AI Product Creator.
Based on market gaps, competitor weaknesses, and trending consumer demands,
invent improved or novel product concepts. Return: concepts[] each with
name, description, target_market, unique_selling_points[], estimated_demand,
estimated_margin_percent, difficulty_score (0-100), innovation_score (0-100)."""

PLATFORM_RECOMMENDER_PROMPT = """You are SellerVision AI's Platform Recommendation Engine.
Given a product and cross-platform data, rank all platforms and recommend the best.
Score each platform: demand_score, competition_score, fee_score, profit_score,
ad_cost_score, customer_intent_score, return_rate_score, overall_score.
Return: platform_rankings[] sorted by overall_score, best_platform, reasoning."""

LAUNCH_SIMULATOR_PROMPT = """You are SellerVision AI's Product Launch Simulator.
Simulate a product launch across multiple scenarios. Given the inputs, predict:
For each scenario (conservative, realistic, optimistic):
- Week 1-4 revenue trajectory
- Monthly cash flow for 6 months
- Break-even date
- Total profit at 6 and 12 months
- PPC efficiency curve
- Inventory consumption rate
- ROI

Return structured JSON with all scenarios and a recommended scenario."""


class AIProductService:

    @cached(ttl=1800, key_prefix="opportunity")
    async def calculate_opportunity_score(self, product: Any) -> ProductOpportunityScore:
        if not _ai_available():
            return ProductOpportunityScore(
                opportunity_score=72.0, risk_score=28.0, profit_score=68.0,
                competition_score=41.0, market_entry_score=65.0,
                prediction_30d_units=145, prediction_90d_units=480, prediction_180d_units=1020,
                prediction_12m_revenue=48500.0,
                reasoning="Demo mode â€” add Anthropic API key for live opportunity scoring.",
                action_recommendation="Strong opportunity. Consider launching in Q3 with $50/day PPC budget.",
            )
        prompt = f"""Analyze this product and return opportunity scores as JSON:
Product: {json.dumps(product, default=str)}

Return JSON with keys:
opportunity_score (0-100), risk_score (0-100), profit_score (0-100),
competition_score (0-100), market_entry_score (0-100),
prediction_30d_units, prediction_90d_units, prediction_180d_units,
prediction_12m_revenue, reasoning (string), action_recommendation (string)"""

        message = await _get_anthropic().messages.create(
            model=settings.ANTHROPIC_MODEL,
            max_tokens=1024,
            system=OPPORTUNITY_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}]
        )
        data = json.loads(message.content[0].text)
        return ProductOpportunityScore(**data)

    async def predict_success(self, concept: dict) -> ProductSuccessPrediction:
        if not _ai_available():
            return ProductSuccessPrediction(
                success_probability=68.0,
                estimated_revenue_monthly=5800.0, estimated_profit_monthly=1740.0,
                break_even_months=4,
                risk_factors=["Increasing competition", "PPC costs rising", "Seasonal demand"],
                opportunities=["Low review count gap", "Weak competitor listings", "Rising search trend"],
                recommendation="launch",
                explainable_reasoning="Demo mode â€” add Anthropic API key for live success prediction.",
            )
        prompt = f"""Predict success for this product concept:
{json.dumps(concept, indent=2)}

Market context: Include realistic estimates based on category benchmarks."""

        message = await _get_anthropic().messages.create(
            model=settings.ANTHROPIC_MODEL,
            max_tokens=2048,
            system=SUCCESS_PREDICTOR_PROMPT,
            messages=[{"role": "user", "content": prompt}]
        )
        data = json.loads(message.content[0].text)
        return ProductSuccessPrediction(**data)

    async def analyze_saturation(self, category: str, marketplace: str) -> SaturationRadar:
        if not _ai_available():
            return SaturationRadar(
                current_saturation_score=42.0, saturation_3m=48.0, saturation_6m=54.0, saturation_12m=61.0,
                new_seller_velocity="moderate", review_velocity_trend="increasing",
                entry_risk_score=38.0, exit_risk_score=22.0,
                heat_map_data=[{"segment": "premium", "score": 35}, {"segment": "budget", "score": 72}, {"segment": "mid-range", "score": 48}],
                recommendation="Good entry window for the premium segment. Avoid budget tier â€” heavily saturated.",
            )
        prompt = f"""Analyze market saturation for:
Category: {category}
Marketplace: {marketplace}
Include new seller entry rates, review velocity, listing growth, and PPC inflation trends."""

        message = await _get_anthropic().messages.create(
            model=settings.ANTHROPIC_MODEL,
            max_tokens=2048,
            system=SATURATION_PROMPT,
            messages=[{"role": "user", "content": prompt}]
        )
        data = json.loads(message.content[0].text)
        return SaturationRadar(**data)

    async def scan_competitor_weaknesses(self, product: Any) -> dict:
        if not _ai_available():
            return {
                "weaknesses": [
                    {"issue": "Poor packaging â€” breaks during shipping", "frequency": "high", "sentiment_score": -0.82},
                    {"issue": "Instructions unclear / missing", "frequency": "medium", "sentiment_score": -0.61},
                    {"issue": "Color fades quickly", "frequency": "medium", "sentiment_score": -0.74},
                ],
                "opportunities": [
                    {"opportunity": "Reinforce packaging with double-wall box", "potential_impact": "high"},
                    {"opportunity": "Include QR code to video tutorial", "potential_impact": "medium"},
                    {"opportunity": "Use UV-resistant materials", "potential_impact": "medium"},
                ],
                "differentiation_strategies": ["Premium packaging", "Better instructions", "UV coating"],
                "competitive_advantage_score": 71,
                "mode": "demo",
            }
        prompt = f"""Scan competitor weaknesses for product: {json.dumps(product, default=str)}
Focus on top 10 competitors. Mine review data for patterns."""

        message = await _get_anthropic().messages.create(
            model=settings.ANTHROPIC_MODEL,
            max_tokens=3000,
            system=WEAKNESS_SCANNER_PROMPT,
            messages=[{"role": "user", "content": prompt}]
        )
        return json.loads(message.content[0].text)

    async def create_product_concept(self, category: str) -> dict:
        if not _ai_available():
            return {
                "concepts": [
                    {"name": f"Smart {category.title()} Organizer", "description": "AI-designed multi-compartment system with modular expansion", "target_market": "Home organizers aged 25-45", "unique_selling_points": ["Stackable design", "BPA-free materials", "Lifetime warranty"], "estimated_demand": "high", "estimated_margin_percent": 42, "difficulty_score": 35, "innovation_score": 68},
                    {"name": f"Eco {category.title()} Kit", "description": "Sustainable bamboo alternative with premium finish", "target_market": "Eco-conscious buyers", "unique_selling_points": ["100% biodegradable", "Minimalist aesthetic", "Gift-ready packaging"], "estimated_demand": "medium", "estimated_margin_percent": 55, "difficulty_score": 28, "innovation_score": 74},
                ],
                "mode": "demo",
            }
        prompt = f"""Create innovative product concepts for category: {category}
Analyze market gaps, customer pain points, and emerging trends to generate 3-5 concepts."""

        message = await _get_anthropic().messages.create(
            model=settings.ANTHROPIC_MODEL,
            max_tokens=3000,
            system=PRODUCT_CREATOR_PROMPT,
            messages=[{"role": "user", "content": prompt}]
        )
        return json.loads(message.content[0].text)

    async def recommend_best_platform(self, product: Any, comparison: dict) -> dict:
        if not _ai_available():
            return {
                "platform_rankings": [
                    {"platform": "amazon", "demand_score": 88, "competition_score": 62, "fee_score": 55, "profit_score": 71, "overall_score": 82},
                    {"platform": "walmart", "demand_score": 72, "competition_score": 41, "fee_score": 74, "profit_score": 78, "overall_score": 76},
                    {"platform": "shopify", "demand_score": 58, "competition_score": 82, "fee_score": 91, "profit_score": 85, "overall_score": 68},
                ],
                "best_platform": "amazon",
                "reasoning": "Amazon offers the highest demand and established trust. Demo mode â€” add API key for live analysis.",
                "mode": "demo",
            }
        prompt = f"""Recommend best platform for:
Product: {json.dumps(product, default=str)}
Cross-platform data: {json.dumps(comparison)}"""

        message = await _get_anthropic().messages.create(
            model=settings.ANTHROPIC_MODEL,
            max_tokens=2048,
            system=PLATFORM_RECOMMENDER_PROMPT,
            messages=[{"role": "user", "content": prompt}]
        )
        return json.loads(message.content[0].text)

    async def simulate_launch(self, input_data: LaunchSimulatorInput) -> LaunchSimulatorResult:
        if not _ai_available():
            from app.schemas.product import LaunchScenario
            price = input_data.selling_price
            cost = input_data.product_cost
            margin = (price - cost) / price
            return LaunchSimulatorResult(
                scenarios={
                    "conservative": LaunchScenario(scenario="conservative", weekly_revenue=[price*20, price*35, price*55, price*70], monthly_cash_flow=[-2000, -800, 400, 1200, 1800, 2400], break_even_date="2026-10-01", profit_6m=round(price*180*margin - 3000, 0), profit_12m=round(price*500*margin - 5000, 0), roi_percent=round((price*500*margin - 5000) / (cost * input_data.inventory_quantity) * 100, 1), inventory_depleted_date="2027-02-01"),
                    "realistic": LaunchScenario(scenario="realistic", weekly_revenue=[price*35, price*65, price*95, price*120], monthly_cash_flow=[-1500, 200, 1400, 2800, 3600, 4200], break_even_date="2026-08-15", profit_6m=round(price*315*margin - 2000, 0), profit_12m=round(price*900*margin - 3000, 0), roi_percent=round((price*900*margin - 3000) / (cost * input_data.inventory_quantity) * 100, 1), inventory_depleted_date="2026-12-01"),
                    "optimistic": LaunchScenario(scenario="optimistic", weekly_revenue=[price*60, price*110, price*160, price*200], monthly_cash_flow=[500, 2200, 3800, 5400, 6800, 7500], break_even_date="2026-07-20", profit_6m=round(price*530*margin - 1000, 0), profit_12m=round(price*1400*margin - 1500, 0), roi_percent=round((price*1400*margin - 1500) / (cost * input_data.inventory_quantity) * 100, 1), inventory_depleted_date="2026-10-15"),
                },
                recommended_scenario="realistic",
                key_assumptions=["30-day launch ramp", f"${input_data.ppc_budget_daily}/day PPC throughout", "No stockouts", "4.2â˜… review average by month 3"],
                warnings=["Demo mode â€” add Anthropic API key for AI-powered simulation", "Actual results vary based on category, competition, and seasonality"],
            )
        prompt = f"""Simulate product launch with these parameters:
Product Cost: ${input_data.product_cost}
Inventory: {input_data.inventory_quantity} units
PPC Budget: ${input_data.ppc_budget_daily}/day
Selling Price: ${input_data.selling_price}
Marketplace: {input_data.marketplace}
Category BSR Target: {input_data.target_bsr}
Launch Strategy: {input_data.launch_strategy}"""

        message = await _get_anthropic().messages.create(
            model=settings.ANTHROPIC_MODEL,
            max_tokens=4096,
            system=LAUNCH_SIMULATOR_PROMPT,
            messages=[{"role": "user", "content": prompt}]
        )
        data = json.loads(message.content[0].text)
        return LaunchSimulatorResult(**data)
