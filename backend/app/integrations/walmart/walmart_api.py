"""
Walmart Marketplace API Integration
Docs: https://developer.walmart.com/
"""
import httpx
import base64
import time
import uuid
from typing import Optional
from app.core.config import settings
from app.core.cache import cached, cache_set, cache_get

WALMART_BASE = "https://marketplace.walmartapis.com/v3"


class WalmartAPI:
    def __init__(self, tenant_slug: str = None):
        self.tenant_slug = tenant_slug
        self._token: Optional[str] = None

    async def _get_token(self) -> str:
        cache_key = f"walmart_token:{self.tenant_slug or 'default'}"
        cached_token = await cache_get(cache_key)
        if cached_token:
            return cached_token
        credentials = base64.b64encode(
            f"{settings.WALMART_CLIENT_ID}:{settings.WALMART_CLIENT_SECRET}".encode()
        ).decode()
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://marketplace.walmartapis.com/v3/token",
                headers={
                    "Authorization": f"Basic {credentials}",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "WM_SVC.NAME": "Walmart Marketplace",
                    "WM_QOS.CORRELATION_ID": str(uuid.uuid4()),
                },
                data={"grant_type": "client_credentials"},
            )
            resp.raise_for_status()
            token = resp.json()["access_token"]
            await cache_set(cache_key, token, ttl=3500)
            return token

    async def _request(self, method: str, path: str, params: dict = None, body: dict = None) -> dict:
        token = await self._get_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "WM_SVC.NAME": "Walmart Marketplace",
            "WM_QOS.CORRELATION_ID": str(uuid.uuid4()),
            "WM_SEC.ACCESS_TOKEN": token,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.request(
                method, f"{WALMART_BASE}{path}",
                headers=headers, params=params, json=body
            )
            resp.raise_for_status()
            return resp.json()

    @cached(ttl=3600, key_prefix="walmart_search")
    async def search_catalog(self, query: str, category: str = "", max_results: int = 20) -> dict:
        return await self._request("GET", "/items/walmart/search", params={
            "query": query, "numItems": min(max_results, 25), "categoryId": category or None,
        })

    @cached(ttl=1800, key_prefix="walmart_item")
    async def get_item(self, item_id: str) -> dict:
        return await self._request("GET", f"/items/{item_id}")

    async def get_my_items(self, limit: int = 20, offset: int = 0) -> dict:
        return await self._request("GET", "/items", params={"limit": limit, "offset": offset})

    async def get_orders(self, days_back: int = 30) -> dict:
        from datetime import datetime, timedelta
        created_start = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%dT%H:%M:%SZ")
        return await self._request("GET", "/orders", params={"createdStartDate": created_start, "limit": 100})

    async def get_inventory(self, sku: str = None) -> dict:
        params = {}
        if sku:
            params["sku"] = sku
        return await self._request("GET", "/inventory", params=params)

    async def publish_listing(self, listing_id: str) -> dict:
        from app.core.database import tenant_session
        from app.models.remaining_models import Listing
        from sqlalchemy import select
        async with tenant_session(self.tenant_slug) as db:
            result = await db.execute(select(Listing).where(Listing.id == listing_id))
            listing = result.scalar_one_or_none()
        if not listing:
            raise ValueError(f"Listing {listing_id} not found")
        item_payload = {
            "MPItem": [{
                "processMode": "CREATE",
                "sku": listing_id,
                "productIdentifiers": {"productIdentifierType": "GTIN", "productIdentifier": ""},
                "MPOffer": {"currentPrice": {"currency": "USD", "amount": float(listing.price or 0)},
                            "fulfillmentLagTime": 1, "startDate": "", "endDate": ""},
                "productName": listing.title,
                "shortDescription": listing.description[:1000] if listing.description else "",
            }]
        }
        return await self._request("POST", "/feeds?feedType=MP_ITEM", body=item_payload)

    async def get_price_analytics(self, sku: str) -> dict:
        return await self._request("GET", f"/priceanalysis/{sku}")

    async def update_price(self, sku: str, price: float) -> dict:
        body = {"prices": [{"pricing": [{"currentPriceType": "BASE",
                "currentPrice": {"currency": "USD", "amount": price}}], "sku": sku}]}
        return await self._request("PUT", "/prices", body=body)
