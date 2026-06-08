"""Module 8: Advanced Keyword Intelligence."""
import json
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.cache import cached

def _get_anthropic():
    from anthropic import AsyncAnthropic
    return AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY or "placeholder")

from app.core.ai_utils import ai_available as _ai_available

KEYWORD_SYSTEM = """You are SellerVision AI's Keyword Intelligence Engine.
Provide precise, data-driven keyword analysis for e-commerce.
Return structured JSON with real-world accuracy for search volumes, CPC, and difficulty.
Use Amazon, Google, and marketplace data patterns."""


class KeywordService:
    def __init__(self, db: AsyncSession = None, tenant_slug: str = None):
        self.db = db
        self.tenant_slug = tenant_slug

    @cached(ttl=3600, key_prefix="kw_research")
    async def research_keyword(
        self, keyword: str, marketplace: str, include_related: bool, include_long_tail: bool
    ) -> dict:
        if not _ai_available():
            return {
                "keyword": keyword, "marketplace": marketplace,
                "monthly_searches": 42000, "search_volume_trend": 8.5,
                "cpc": 1.24, "competition_level": "medium",
                "difficulty_score": 38, "opportunity_score": 74,
                "ppc_score": 65, "seo_score": 71,
                "intent": "commercial",
                "related_keywords": [
                    {"keyword": f"{keyword} for sale", "volume": 12000},
                    {"keyword": f"best {keyword}", "volume": 8500},
                    {"keyword": f"{keyword} reviews", "volume": 5200},
                ],
                "long_tail_keywords": [
                    {"keyword": f"best {keyword} for home use", "volume": 2400, "difficulty": 22},
                    {"keyword": f"affordable {keyword} online", "volume": 1800, "difficulty": 18},
                ],
                "top_ranking_asins": ["B08N5WRWNW", "B09G9FPHY6", "B07ZPKN6YR", "B08KHX8QJV", "B089NQPJ2D"],
                "ai_insights": "Demo mode â€” add Anthropic API key for live keyword intelligence.",
                "mode": "demo",
            }
        prompt = f"""Research this keyword for {marketplace}:
Keyword: "{keyword}"

Return JSON with:
- keyword, marketplace
- monthly_searches (integer), search_volume_trend (% change last 30d)
- cpc (float, USD), competition_level (low/medium/high)
- difficulty_score (0-100), opportunity_score (0-100)
- ppc_score (0-100), seo_score (0-100)
- intent (informational/navigational/transactional/commercial)
- related_keywords (array of top 10 related with volume)
- long_tail_keywords (array of 15 long-tail with volume and difficulty)
- top_ranking_asins (array of 5 ASINs currently ranking)
- ai_insights (string with actionable recommendation)"""

        msg = await _get_anthropic().messages.create(
            model=settings.ANTHROPIC_MODEL, max_tokens=2000,
            system=KEYWORD_SYSTEM, messages=[{"role": "user", "content": prompt}]
        )
        return json.loads(msg.content[0].text)

    @cached(ttl=1800, key_prefix="kw_bulk")
    async def research_bulk(self, keywords: List[str], marketplace: str) -> List[dict]:
        import asyncio
        tasks = [self.research_keyword(kw, marketplace, False, False) for kw in keywords[:50]]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [r for r in results if not isinstance(r, Exception)]

    async def cluster_keywords(self, keywords: List[str]) -> dict:
        if not _ai_available():
            return {
                "clusters": [{"topic": "Primary", "intent": "commercial", "keywords": keywords[:5], "total_volume_estimate": 50000, "avg_difficulty": 35.0, "commercial_value": "high"}],
                "primary_cluster": "Primary",
                "total_keywords": len(keywords),
                "mode": "demo",
            }
        prompt = f"""Cluster these keywords into semantic groups:
{json.dumps(keywords)}

Return JSON: {{
  "clusters": [
    {{
      "topic": "string",
      "intent": "informational|transactional|commercial",
      "keywords": ["kw1", "kw2"],
      "total_volume_estimate": integer,
      "avg_difficulty": float,
      "commercial_value": "high|medium|low"
    }}
  ],
  "primary_cluster": "string",
  "total_keywords": integer
}}"""
        msg = await _get_anthropic().messages.create(
            model=settings.ANTHROPIC_MODEL, max_tokens=2000,
            system=KEYWORD_SYSTEM, messages=[{"role": "user", "content": prompt}]
        )
        return json.loads(msg.content[0].text)

    @cached(ttl=3600, key_prefix="reverse_asin")
    async def reverse_asin_lookup(self, asin: str, marketplace: str) -> dict:
        """Get all keywords an ASIN ranks for."""
        if not _ai_available():
            return {
                "asin": asin, "total_keywords_estimate": 847,
                "organic_keywords": [
                    {"keyword": "kitchen organizer", "rank": 3, "search_volume": 45000, "relevance_score": 0.95},
                    {"keyword": "drawer organizer set", "rank": 7, "search_volume": 22000, "relevance_score": 0.88},
                    {"keyword": "home storage solutions", "rank": 12, "search_volume": 18000, "relevance_score": 0.72},
                ],
                "sponsored_keywords": [
                    {"keyword": "kitchen storage", "rank": 2, "search_volume": 60000, "relevance_score": 0.91},
                ],
                "high_value_keywords": [{"keyword": "kitchen organizer", "rank": 3, "search_volume": 45000, "relevance_score": 0.95}],
                "missing_opportunities": [{"keyword": "bamboo drawer divider", "search_volume": 12000, "relevance_score": 0.85}],
                "mode": "demo",
            }
        from app.integrations.amazon.sp_api import AmazonSPAPI
        api = AmazonSPAPI()
        product_data = await api.get_catalog_item(asin)

        prompt = f"""Based on this Amazon product, predict all keywords it likely ranks for:
ASIN: {asin}
Product data: {json.dumps(product_data, default=str)[:2000]}

Return JSON: {{
  "asin": "{asin}",
  "total_keywords_estimate": integer,
  "organic_keywords": [
    {{"keyword": "...", "rank": integer, "search_volume": integer, "relevance_score": float}}
  ],
  "sponsored_keywords": [...same structure...],
  "high_value_keywords": [...top 5 by volume...],
  "missing_opportunities": [...keywords not ranking but highly relevant...]
}}"""
        msg = await _get_anthropic().messages.create(
            model=settings.ANTHROPIC_MODEL, max_tokens=3000,
            system=KEYWORD_SYSTEM, messages=[{"role": "user", "content": prompt}]
        )
        return json.loads(msg.content[0].text)

    async def find_opportunities(
        self, category: Optional[str], min_volume: int, max_difficulty: float, marketplace: str
    ) -> list:
        if not _ai_available():
            return [
                {"keyword": "bamboo kitchen organizer", "monthly_searches": 28000, "difficulty_score": 31, "opportunity_score": 82, "cpc": 0.98, "reasoning": "Low competition, high demand"},
                {"keyword": "silicone food storage bags", "monthly_searches": 52000, "difficulty_score": 38, "opportunity_score": 78, "cpc": 1.45, "reasoning": "Growing eco-friendly trend"},
                {"keyword": "over door shoe organizer", "monthly_searches": 35000, "difficulty_score": 29, "opportunity_score": 76, "cpc": 0.87, "reasoning": "Evergreen home organization niche"},
            ]
        prompt = f"""Find keyword opportunities in {marketplace}{' for ' + category if category else ''}:
Criteria: min {min_volume:,} monthly searches, max {max_difficulty} difficulty

Return JSON array of 20 opportunities, each with:
keyword, monthly_searches, difficulty_score, opportunity_score, cpc, reasoning"""
        msg = await _get_anthropic().messages.create(
            model=settings.ANTHROPIC_MODEL, max_tokens=2000,
            system=KEYWORD_SYSTEM, messages=[{"role": "user", "content": prompt}]
        )
        return json.loads(msg.content[0].text)

    async def get_trending_keywords(self, marketplace: str, period: str) -> list:
        if not _ai_available():
            return [
                {"keyword": "Stanley tumbler", "search_volume": 180000, "growth_percent": 340, "category": "drinkware", "opportunity_score": 71},
                {"keyword": "air fryer liner", "search_volume": 95000, "growth_percent": 128, "category": "kitchen", "opportunity_score": 84},
                {"keyword": "wireless charging pad", "search_volume": 72000, "growth_percent": 65, "category": "electronics", "opportunity_score": 69},
                {"keyword": "LED strip lights", "search_volume": 210000, "growth_percent": 42, "category": "lighting", "opportunity_score": 55},
                {"keyword": "yoga mat strap", "search_volume": 38000, "growth_percent": 89, "category": "fitness", "opportunity_score": 77},
            ]
        prompt = f"""List top 20 trending keywords on {marketplace} in {period}.
Include: keyword, search_volume, growth_percent, category, opportunity_score.
Return as JSON array."""
        msg = await _get_anthropic().messages.create(
            model=settings.ANTHROPIC_MODEL, max_tokens=1500,
            system=KEYWORD_SYSTEM, messages=[{"role": "user", "content": prompt}]
        )
        return json.loads(msg.content[0].text)

    async def get_keyword_history(self, keyword_id, days: int) -> list:
        if not self.db:
            return []
        from sqlalchemy import select, desc
        from datetime import datetime, timedelta
        from app.models.keyword import KeywordMetric
        cutoff = datetime.utcnow() - timedelta(days=days)
        result = await self.db.execute(
            select(KeywordMetric)
            .where(KeywordMetric.keyword_id == keyword_id, KeywordMetric.time >= cutoff)
            .order_by(desc(KeywordMetric.time))
        )
        return result.scalars().all()

    async def track_all_ranks(self) -> None:
        """Background task: update keyword rankings for all tracked products."""
        pass  # Implemented in worker via SP-API reports
