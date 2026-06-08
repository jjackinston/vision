"""
Amazon Selling Partner API Integration
Covers: Catalog, Orders, Inventory, Advertising, Reports
"""
import httpx
import hashlib
import hmac
import json
from datetime import datetime, timezone
from typing import Optional, List
from urllib.parse import urlencode, quote

from app.core.config import settings
from app.core.cache import cached, cache_set, cache_get

SP_API_BASE = "https://sellingpartnerapi-na.amazon.com"
AUTH_URL = "https://api.amazon.com/auth/o2/token"
REGION = "us-east-1"
SERVICE = "execute-api"


class AmazonSPAPI:

    def __init__(self, marketplace_id: str = None, tenant_slug: str = None):
        self.marketplace_id = marketplace_id or settings.AMAZON_MARKETPLACE_ID
        self.tenant_slug = tenant_slug
        self._access_token: Optional[str] = None

    async def _get_access_token(self) -> str:
        cache_key = f"amazon_token:{self.tenant_slug or 'default'}"
        cached_token = await cache_get(cache_key)
        if cached_token:
            return cached_token

        async with httpx.AsyncClient() as client:
            resp = await client.post(AUTH_URL, data={
                "grant_type": "refresh_token",
                "refresh_token": settings.AMAZON_REFRESH_TOKEN,
                "client_id": settings.AMAZON_CLIENT_ID,
                "client_secret": settings.AMAZON_CLIENT_SECRET,
            })
            resp.raise_for_status()
            data = resp.json()
            token = data["access_token"]
            await cache_set(cache_key, token, ttl=3500)
            return token

    async def _signed_request(self, method: str, path: str, params: dict = None, body: dict = None) -> dict:
        token = await self._get_access_token()
        url = f"{SP_API_BASE}{path}"
        headers = {
            "x-amz-access-token": token,
            "x-amz-date": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
            "Content-Type": "application/json",
            "User-Agent": "SellerVisionAI/1.0",
        }
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.request(
                method,
                url,
                params=params,
                json=body,
                headers=headers,
            )
            resp.raise_for_status()
            return resp.json()

    @cached(ttl=3600, key_prefix="amazon_search")
    async def search_catalog(self, query: str, category: str = "", max_results: int = 20) -> dict:
        """Search Amazon catalog items."""
        params = {
            "keywords": query,
            "marketplaceIds": self.marketplace_id,
            "pageSize": min(max_results, 20),
        }
        if category:
            params["classification"] = category
        return await self._signed_request("GET", "/catalog/2022-04-01/items", params=params)

    @cached(ttl=1800, key_prefix="amazon_asin")
    async def get_catalog_item(self, asin: str) -> dict:
        """Get detailed catalog data for an ASIN."""
        params = {
            "marketplaceIds": self.marketplace_id,
            "includedData": "attributes,dimensions,images,productTypes,relationships,salesRanks,summaries",
        }
        return await self._signed_request("GET", f"/catalog/2022-04-01/items/{asin}", params=params)

    @cached(ttl=900, key_prefix="amazon_offers")
    async def get_competitive_pricing(self, asin: str) -> dict:
        """Get buy box and competitive pricing."""
        params = {"MarketplaceId": self.marketplace_id, "Asins": asin}
        return await self._signed_request("GET", "/products/pricing/v0/competitivePrice", params=params)

    async def get_my_inventory(self, sku: str = None) -> dict:
        """Get FBA inventory levels."""
        params = {
            "details": "true",
            "granularityType": "Marketplace",
            "granularityId": self.marketplace_id,
        }
        if sku:
            params["sellerSkus"] = sku
        return await self._signed_request("GET", "/fba/inventory/v1/summaries", params=params)

    async def get_orders(self, days_back: int = 30) -> dict:
        """Get recent orders."""
        from datetime import timedelta
        created_after = (datetime.now(timezone.utc) - timedelta(days=days_back)).isoformat()
        params = {
            "MarketplaceIds": self.marketplace_id,
            "CreatedAfter": created_after,
        }
        return await self._signed_request("GET", "/orders/v0/orders", params=params)

    async def get_reviews(self, asin: str, max_reviews: int = 100) -> list:
        """
        Get product reviews.
        Note: SP-API does not provide direct review access — this uses
        the Product Reviews report or a compliant third-party data source.
        In production, integrate with a licensed data provider.
        """
        # Placeholder — integrate with licensed review data provider
        return [
            {
                "asin": asin,
                "rating": 3,
                "title": "Sample review",
                "body": "Product works but could be better",
                "verified": True,
                "date": "2025-01-15",
            }
        ]

    async def get_sales_rank_history(self, asin: str) -> dict:
        """Get BSR history via reports API."""
        # Request a GET_MERCHANT_LISTINGS_ALL_DATA report
        body = {
            "reportType": "GET_MERCHANT_LISTINGS_ALL_DATA",
            "marketplaceIds": [self.marketplace_id],
        }
        report_resp = await self._signed_request("POST", "/reports/2021-06-30/reports", body=body)
        return report_resp

    async def submit_listing(self, sku: str, listing_data: dict) -> dict:
        """Submit/update a product listing."""
        return await self._signed_request(
            "PUT",
            f"/listings/2021-08-01/items/{settings.AMAZON_CLIENT_ID}/{sku}",
            params={"marketplaceIds": self.marketplace_id},
            body=listing_data,
        )

    async def publish_listing(self, listing_id: str) -> dict:
        """Push a SellerVision listing to Amazon."""
        from app.core.database import tenant_session
        from app.models.listing import Listing
        from sqlalchemy import select

        async with tenant_session(self.tenant_slug) as db:
            result = await db.execute(select(Listing).where(Listing.id == listing_id))
            listing = result.scalar_one_or_none()

        if not listing:
            raise ValueError(f"Listing {listing_id} not found")

        listing_data = {
            "productType": "HOME",
            "attributes": {
                "item_name": [{"value": listing.title}],
                "bullet_point": [{"value": bp} for bp in (listing.bullet_points or [])],
                "product_description": [{"value": listing.description}],
                "list_price": [{"value": float(listing.price), "currency": "USD"}],
            }
        }
        return await self.submit_listing(listing.sku, listing_data)
