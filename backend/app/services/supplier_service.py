"""Module 12: Supplier Intelligence + Module 13: AI Negotiation Assistant."""
import json
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings

def _get_anthropic():
    from anthropic import AsyncAnthropic
    return AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY or "placeholder")

from app.core.ai_utils import ai_available as _ai_available

SUPPLIER_SYSTEM = """You are SellerVision AI's Supplier Intelligence Engine.
Analyze suppliers for e-commerce businesses. Provide trust scores, risk assessments,
cost optimization strategies, and negotiation intelligence.
Be precise and commercially focused."""

NEGOTIATION_SYSTEM = """You are SellerVision AI's AI Negotiation Assistant.
You help e-commerce sellers negotiate better prices, MOQs, and terms with suppliers.
Generate professional, culturally-appropriate negotiation scripts and strategies.
Focus on win-win outcomes while maximizing buyer leverage."""


class SupplierService:
    def __init__(self, db: AsyncSession = None, tenant_slug: str = None):
        self.db = db
        self.tenant_slug = tenant_slug

    async def list_suppliers(self, country=None, min_trust_score=None):
        from app.models.remaining_models import Supplier
        from sqlalchemy import select
        q = select(Supplier)
        if country:
            q = q.where(Supplier.country == country)
        if min_trust_score:
            q = q.where(Supplier.trust_score >= min_trust_score)
        result = await self.db.execute(q)
        return result.scalars().all()

    async def analyze_supplier(self, name: str, country: str, website: Optional[str] = None) -> dict:
        if not _ai_available():
            data = {
                "trust_score": 74, "risk_score": 32, "quality_score": 78,
                "reliability_score": 71, "avg_lead_time_days": 28, "min_order_qty": 500,
                "payment_terms": "30% deposit, 70% before shipment",
                "shipping_methods": ["Sea freight", "Air freight", "DDP"],
                "certifications": ["ISO 9001", "CE", "RoHS"],
                "risk_factors": ["Lead time variability", "Communication delays", "Currency fluctuation"],
                "strengths": ["Competitive pricing", "High capacity", "Wide product range"],
                "negotiation_leverage_points": ["Volume commitment", "Longer payment terms", "Repeat business"],
                "recommended_due_diligence": ["Request samples", "Factory audit", "Trade reference check"],
                "ai_summary": f"Demo analysis for {name} in {country}. Add Anthropic API key for live supplier intelligence.",
                "mode": "demo",
            }
            if self.db:
                from app.models.remaining_models import Supplier
                supplier = Supplier(
                    name=name, country=country, website=website,
                    trust_score=data["trust_score"], risk_score=data["risk_score"],
                    quality_score=data["quality_score"], reliability_score=data["reliability_score"],
                    avg_lead_time_days=data["avg_lead_time_days"], min_order_qty=data["min_order_qty"],
                    payment_terms=data["payment_terms"], ai_analysis=data,
                )
                self.db.add(supplier)
                await self.db.commit()
                data["supplier_id"] = str(supplier.id)
            return data
        prompt = f"""Analyze this supplier for an e-commerce business:
Name: {name}
Country: {country}
Website: {website or 'unknown'}

Return JSON with:
- trust_score (0-100): based on typical {country} supplier reliability
- risk_score (0-100): supply chain risk assessment
- quality_score (0-100): expected product quality
- reliability_score (0-100): on-time delivery reliability
- avg_lead_time_days: realistic estimate
- min_order_qty: typical MOQ for this type of supplier
- payment_terms: recommended payment structure
- shipping_methods: available options
- certifications: likely certifications
- risk_factors: array of specific risks
- strengths: array of advantages
- negotiation_leverage_points: where buyer has power
- recommended_due_diligence: steps to verify this supplier
- ai_summary: 2-sentence overall assessment"""

        msg = await _get_anthropic().messages.create(
            model=settings.ANTHROPIC_MODEL, max_tokens=2000,
            system=SUPPLIER_SYSTEM, messages=[{"role": "user", "content": prompt}]
        )
        data = json.loads(msg.content[0].text)

        if self.db:
            from app.models.remaining_models import Supplier
            supplier = Supplier(
                name=name, country=country, website=website,
                trust_score=data.get("trust_score"),
                risk_score=data.get("risk_score"),
                quality_score=data.get("quality_score"),
                reliability_score=data.get("reliability_score"),
                avg_lead_time_days=data.get("avg_lead_time_days"),
                min_order_qty=data.get("min_order_qty"),
                payment_terms=data.get("payment_terms"),
                ai_analysis=data,
            )
            self.db.add(supplier)
            await self.db.commit()
            data["supplier_id"] = str(supplier.id)
        return data

    async def generate_negotiation_script(
        self, supplier_id: str, goal: str,
        current_price: float, target_price: float,
        current_moq: int, target_moq: int
    ) -> dict:
        price_reduction = ((current_price - target_price) / current_price) * 100
        moq_reduction = ((current_moq - target_moq) / current_moq) * 100

        if not _ai_available():
            return {
                "opening_email": f"Dear [Supplier], We are interested in establishing a long-term partnership. We are targeting ${target_price:.2f} per unit with MOQ of {target_moq:,} units.",
                "negotiation_script": [
                    {"phase": "opening", "script": "Express long-term partnership interest", "psychological_principle": "Reciprocity"},
                    {"phase": "anchor", "script": f"Reference market price of ${target_price:.2f}", "psychological_principle": "Anchoring"},
                    {"phase": "counter", "script": "Offer volume commitment in exchange for price reduction", "psychological_principle": "Concession"},
                    {"phase": "close", "script": "Set timeline and next steps", "psychological_principle": "Scarcity"},
                ],
                "leverage_points": ["Volume commitment", "Fast payment", "Long-term contract"],
                "concession_strategy": "Offer 10% volume increase in exchange for 5% price reduction",
                "fallback_positions": [f"${current_price * 0.95:.2f}", f"${current_price * 0.97:.2f}"],
                "red_lines": ["Never reveal maximum budget", "Don't accept first offer"],
                "success_probability": 0.68,
                "estimated_achievable_price": round(current_price * 0.93, 2),
                "estimated_achievable_moq": int(target_moq * 1.1),
                "mode": "demo",
            }
        prompt = f"""Generate a complete supplier negotiation strategy:

Goal: {goal}
Current Price: ${current_price} â†’ Target: ${target_price} ({price_reduction:.1f}% reduction)
Current MOQ: {current_moq} â†’ Target: {target_moq} ({moq_reduction:.1f}% reduction)

Return JSON: {{
  "opening_email": "full email text",
  "negotiation_script": [
    {{"phase": "opening", "script": "...", "psychological_principle": "..."}},
    {{"phase": "anchor", "script": "...", "psychological_principle": "..."}},
    {{"phase": "counter", "script": "...", "psychological_principle": "..."}},
    {{"phase": "close", "script": "...", "psychological_principle": "..."}}
  ],
  "leverage_points": ["..."],
  "concession_strategy": "...",
  "fallback_positions": ["position1", "position2"],
  "red_lines": ["never do this"],
  "success_probability": float,
  "estimated_achievable_price": float,
  "estimated_achievable_moq": integer
}}"""

        msg = await _get_anthropic().messages.create(
            model=settings.ANTHROPIC_MODEL, max_tokens=3000,
            system=NEGOTIATION_SYSTEM, messages=[{"role": "user", "content": prompt}]
        )
        return json.loads(msg.content[0].text)

    async def analyze_conversation(self, supplier_id: str, conversation: str) -> dict:
        if not _ai_available():
            return {
                "sentiment_analysis": {"buyer": "neutral", "supplier": "positive"},
                "leverage_detected": ["Supplier eager to close", "Price flexibility hinted"],
                "red_flags": ["Vague delivery commitment"],
                "opportunities_missed": ["Did not anchor on volume"],
                "next_message_recommendation": "Follow up on delivery timeline and request written commitment",
                "negotiation_stage": "mid",
                "probability_of_success": 0.72,
                "recommended_next_actions": ["Request samples", "Ask for written price sheet"],
                "mode": "demo",
            }
        prompt = f"""Analyze this supplier conversation and provide negotiation recommendations:

{conversation}

Return JSON: {{
  "sentiment_analysis": {{"buyer": "string", "supplier": "string"}},
  "leverage_detected": ["..."],
  "red_flags": ["..."],
  "opportunities_missed": ["..."],
  "next_message_recommendation": "full message text",
  "negotiation_stage": "initial/mid/closing",
  "probability_of_success": float,
  "recommended_next_actions": ["action1", "action2"]
}}"""
        msg = await _get_anthropic().messages.create(
            model=settings.ANTHROPIC_MODEL, max_tokens=2000,
            system=NEGOTIATION_SYSTEM, messages=[{"role": "user", "content": prompt}]
        )
        return json.loads(msg.content[0].text)

    async def get_risk_report(self, supplier_id: str) -> dict:
        from sqlalchemy import select
        from app.models.remaining_models import Supplier
        result = await self.db.execute(select(Supplier).where(Supplier.id == supplier_id))
        supplier = result.scalar_one_or_none()
        if not supplier:
            return {"error": "Supplier not found"}
        return {
            "supplier": supplier.name,
            "risk_score": float(supplier.risk_score or 0),
            "risk_factors": supplier.ai_analysis.get("risk_factors", []),
            "mitigations": ["Qualify backup supplier", "Increase safety stock"],
            "last_updated": str(supplier.updated_at),
        }

    async def monitor_all(self) -> None:
        """Background: refresh supplier risk scores."""
        pass
