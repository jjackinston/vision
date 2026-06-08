"""
Module 9: AI Listing Builder â€” generates optimized listings for all marketplaces.
Module 15: Multi-Platform Listing Manager â€” publish once, sync everywhere.
"""
import json
from typing import List, Optional
from app.core.config import settings
from app.core.cache import cached

def _get_anthropic():
    from anthropic import AsyncAnthropic
    return AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY or "placeholder")

from app.core.ai_utils import ai_available as _ai_available

LISTING_PROMPTS = {
    "amazon": """Generate an Amazon-optimized product listing. Follow Amazon's style guide:
- Title: 150-200 chars, lead with brand, include top keywords naturally
- 5 Bullet Points: Start each with CAPITALIZED benefit, 200 chars each, feature + benefit
- Description: 2000 chars, story-driven, include all keywords
- Backend Keywords: 250 bytes, no repetition, no punctuation
- A+ Content: Include EBC module recommendations
Return JSON: {title, bullet_points[], description, backend_keywords, a_plus_modules[], seo_score}""",

    "walmart": """Generate a Walmart Marketplace listing:
- Title: 75 chars max, clear and descriptive
- Short Description: 150 chars for mobile
- Long Description: 1000 chars with key features
- Key Features: 3-5 bullet points
Return JSON: {title, short_description, long_description, key_features[], seo_score}""",

    "ebay": """Generate an eBay listing:
- Title: 80 chars, keyword-rich, condition relevant
- Item Specifics: all relevant specs
- Description: HTML-formatted, detailed, trust-building
- Category recommendation
Return JSON: {title, item_specifics{}, description_html, category, seo_score}""",

    "shopify": """Generate a Shopify product page:
- Title: SEO-optimized, natural language
- Meta description: 155 chars for Google
- Description: Rich HTML, benefits-focused, scannable
- Tags: 10-15 relevant tags
Return JSON: {title, meta_description, description_html, tags[], seo_score}""",

    "tiktok": """Generate a TikTok Shop listing optimized for Gen Z discovery:
- Title: Catchy, trend-aware, emoji-friendly, 100 chars
- Description: Conversational, social-proof heavy, 500 chars
- Hashtags: 10 trending + niche hashtags
- Video hook suggestion for content creators
Return JSON: {title, description, hashtags[], video_hook, virality_score}""",

    "etsy": """Generate an Etsy listing optimized for handmade/vintage discovery:
- Title: 140 chars, descriptive, long-tail keyword rich
- Description: Story of the product/maker, 1500 chars
- Tags: exactly 13 tags (Etsy allows 13)
- Materials: list all materials
Return JSON: {title, description, tags[], materials[], seo_score}""",
}


class ListingService:

    async def list_listings(
        self,
        tenant_slug: str,
        marketplace: Optional[str] = None,
        status: Optional[str] = None,
        min_seo_score: Optional[float] = None,
    ) -> list:
        """Return listings from the DB, optionally filtered."""
        from app.core.database import tenant_session
        from app.models.listing import Listing
        from sqlalchemy import select, desc

        async with tenant_session(tenant_slug) as db:
            q = select(Listing).order_by(desc(Listing.seo_score))
            if marketplace:
                q = q.where(Listing.marketplace == marketplace)
            if status:
                q = q.where(Listing.status == status)
            if min_seo_score is not None:
                q = q.where(Listing.seo_score >= min_seo_score)
            result = await db.execute(q)
            listings = result.scalars().all()

        return [
            {
                "id": str(l.id),
                "product_id": str(l.product_id),
                "marketplace": l.marketplace,
                "external_id": l.external_id,
                "title": l.title,
                "bullet_points": l.bullet_points or [],
                "description": l.description,
                "backend_keywords": l.backend_keywords or [],
                "price": float(l.price) if l.price else None,
                "status": l.status,
                "seo_score": float(l.seo_score) if l.seo_score else None,
                "completeness_score": float(l.completeness_score) if l.completeness_score else None,
                "ai_generated": l.ai_generated,
                "published_at": l.published_at.isoformat() if l.published_at else None,
            }
            for l in listings
        ]

    async def audit_seo(
        self,
        listing_id: str,
        marketplace: str,
        tenant_slug: str,
    ) -> dict:
        """Score an existing listing's SEO health."""
        from app.core.database import tenant_session
        from app.models.listing import Listing
        from sqlalchemy import select

        async with tenant_session(tenant_slug) as db:
            result = await db.execute(select(Listing).where(Listing.id == listing_id))
            listing = result.scalar_one_or_none()
            if not listing:
                from fastapi import HTTPException
                raise HTTPException(404, "Listing not found")

        if not _ai_available():
            return {
                "listing_id": listing_id,
                "marketplace": marketplace,
                "seo_score": float(listing.seo_score) if listing.seo_score else 74.0,
                "completeness_score": float(listing.completeness_score) if listing.completeness_score else 82.0,
                "issues": [
                    {"severity": "warning", "field": "backend_keywords", "message": "Some high-volume keywords missing"},
                    {"severity": "info", "field": "description", "message": "Could expand description to 2000 chars"},
                ],
                "opportunities": [
                    "Add seasonal keywords for Q3 campaigns",
                    "Include competitor brand comparisons in backend keywords",
                ],
                "estimated_traffic_lift": "12-18%",
                "mode": "demo",
            }

        prompt = f"""Audit the SEO of this {marketplace} listing:
Title: {listing.title}
Bullet Points: {listing.bullet_points}
Description: {listing.description}
Backend Keywords: {listing.backend_keywords}

Return JSON: {{
  "seo_score": float,
  "completeness_score": float,
  "issues": [{{"severity": "critical|warning|info", "field": "string", "message": "string"}}],
  "opportunities": ["string"],
  "estimated_traffic_lift": "string"
}}"""
        message = await _get_anthropic().messages.create(
            model=settings.ANTHROPIC_MODEL, max_tokens=1500,
            system=LISTING_PROMPTS.get(marketplace, LISTING_PROMPTS["amazon"]),
            messages=[{"role": "user", "content": prompt}]
        )
        return json.loads(message.content[0].text)

    @cached(ttl=86400, key_prefix="listing")
    async def generate_ai_listing(
        self,
        product_data: dict,
        marketplace: str,
        target_keywords: List[str] = None,
        tone: str = "professional",
    ) -> dict:
        if not _ai_available():
            title = product_data.get("title", "Premium Product")
            return {
                "title": f"{title} | High-Quality | Best Value | Fast Shipping",
                "bullet_points": [
                    f"PREMIUM QUALITY â€” {title} built to last with superior materials and craftsmanship",
                    "EASY TO USE â€” Intuitive design that anyone can set up in minutes, no tools required",
                    "VERSATILE â€” Perfect for home, office, or on-the-go use in any environment",
                    "GREAT VALUE â€” Get premium features at an unbeatable price point with full warranty",
                    "CUSTOMER FAVORITE â€” Join thousands of satisfied customers with 4.5â˜… average rating",
                ],
                "description": f"Discover the {title} â€” the all-in-one solution designed for modern lifestyles. Whether you're organizing your home or optimizing your workspace, this product delivers exceptional performance every time.",
                "backend_keywords": (", ".join(target_keywords or [])) or "home organizer storage solution premium quality",
                "seo_score": 74,
                "a_plus_modules": ["comparison_chart", "lifestyle_imagery", "feature_highlights"],
                "mode": "demo",
            }
        system_prompt = LISTING_PROMPTS.get(marketplace, LISTING_PROMPTS["amazon"])

        user_prompt = f"""Create a listing for this product:
{json.dumps(product_data, indent=2)}

Target Keywords: {', '.join(target_keywords or [])}
Tone: {tone}

Ensure all target keywords are naturally incorporated. Optimize for conversion."""

        message = await _get_anthropic().messages.create(
            model=settings.ANTHROPIC_MODEL,
            max_tokens=3000,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )
        return json.loads(message.content[0].text)

    async def generate_multi_platform_listings(
        self,
        product_data: dict,
        marketplaces: List[str],
        target_keywords: List[str] = None,
    ) -> dict:
        """Generate listings for all platforms simultaneously."""
        import asyncio
        tasks = {
            mp: self.generate_ai_listing(product_data, mp, target_keywords)
            for mp in marketplaces
        }
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        return {mp: result for mp, result in zip(tasks.keys(), results)}

    async def optimize_existing_listing(
        self,
        listing_id: str,
        marketplace: str,
        tenant_slug: str,
    ) -> dict:
        """Analyze and improve an existing listing."""
        from app.core.database import tenant_session
        from app.models.listing import Listing
        from sqlalchemy import select

        async with tenant_session(tenant_slug) as db:
            result = await db.execute(select(Listing).where(Listing.id == listing_id))
            listing = result.scalar_one_or_none()
            if not listing:
                raise ValueError(f"Listing {listing_id} not found")

        current_listing = {
            "title": listing.title,
            "bullet_points": listing.bullet_points,
            "description": listing.description,
            "current_seo_score": listing.seo_score,
        }

        if not _ai_available():
            return {"title": "Demo optimized title", "seo_score": 82, "improvements_made": ["Added target keywords to title", "Improved bullet point benefits", "Enhanced description flow"], "mode": "demo"}
        prompt = f"""Analyze and improve this existing {marketplace} listing:
{json.dumps(current_listing)}

Identify weaknesses and generate improved version. Explain each improvement."""

        message = await _get_anthropic().messages.create(
            model=settings.ANTHROPIC_MODEL,
            max_tokens=3000,
            system=LISTING_PROMPTS.get(marketplace, LISTING_PROMPTS["amazon"]) +
                   "\nAlso include: improvements_made[] explaining each change.",
            messages=[{"role": "user", "content": prompt}]
        )
        return json.loads(message.content[0].text)

    async def sync_listing_to_marketplace(
        self,
        listing_id: str,
        marketplace: str,
        tenant_slug: str,
    ) -> dict:
        """Push listing to live marketplace via API."""
        from app.integrations.amazon.sp_api import AmazonSPAPI
        from app.integrations.walmart.walmart_api import WalmartAPI
        from app.integrations.shopify.shopify_api import ShopifyAPI

        connectors = {
            "amazon": AmazonSPAPI,
            "walmart": WalmartAPI,
            "shopify": ShopifyAPI,
        }

        connector_class = connectors.get(marketplace)
        if not connector_class:
            raise ValueError(f"Marketplace {marketplace} not yet supported for live sync")

        connector = connector_class(tenant_slug=tenant_slug)
        return await connector.publish_listing(listing_id)
