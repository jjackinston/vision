"""eBay Sell API Integration — Browse, Inventory, Fulfillment APIs."""
import httpx
import base64
from typing import Optional
from app.core.config import settings
from app.core.cache import cached, cache_get, cache_set

EBAY_API_BASE = "https://api.ebay.com"
EBAY_SANDBOX_BASE = "https://api.sandbox.ebay.com"


class EbayAPI:
    def __init__(self, tenant_slug: str = None, sandbox: bool = False):
        self.tenant_slug = tenant_slug
        self.base = EBAY_SANDBOX_BASE if sandbox else EBAY_API_BASE

    async def _get_app_token(self) -> str:
        cache_key = "ebay_app_token"
        cached_token = await cache_get(cache_key)
        if cached_token:
            return cached_token
        credentials = base64.b64encode(
            f"{settings.EBAY_APP_ID}:{settings.EBAY_CERT_ID}".encode()
        ).decode()
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base}/identity/v1/oauth2/token",
                headers={
                    "Authorization": f"Basic {credentials}",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                data={"grant_type": "client_credentials", "scope": "https://api.ebay.com/oauth/api_scope"},
            )
            resp.raise_for_status()
            token = resp.json()["access_token"]
            expires_in = resp.json().get("expires_in", 7200) - 60
            await cache_set(cache_key, token, ttl=expires_in)
            return token

    async def _request(self, method: str, path: str, params: dict = None, body: dict = None) -> dict:
        token = await self._get_app_token()
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.request(
                method, f"{self.base}{path}",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                params=params, json=body
            )
            resp.raise_for_status()
            return resp.json()

    @cached(ttl=1800, key_prefix="ebay_search")
    async def search_items(self, query: str, category_id: str = None, limit: int = 20) -> dict:
        params = {"q": query, "limit": min(limit, 200)}
        if category_id:
            params["category_ids"] = category_id
        return await self._request("GET", "/buy/browse/v1/item_summary/search", params=params)

    async def get_item(self, item_id: str) -> dict:
        return await self._request("GET", f"/buy/browse/v1/item/{item_id}")

    @cached(ttl=3600, key_prefix="ebay_taxonomy")
    async def get_category_suggestions(self, query: str) -> dict:
        return await self._request("GET", "/commerce/taxonomy/v1/category_tree/0/get_category_suggestions",
                                    params={"q": query})

    async def get_seller_listings(self, seller: str = None, limit: int = 50) -> dict:
        params = {"limit": limit}
        return await self._request("GET", "/sell/inventory/v1/inventory_item", params=params)

    async def create_listing(self, listing_data: dict) -> dict:
        sku = listing_data.get("sku", str(__import__("uuid").uuid4()))
        inventory_item = {
            "availability": {"shipToLocationAvailability": {"quantity": listing_data.get("quantity", 1)}},
            "condition": listing_data.get("condition", "NEW"),
            "product": {
                "title": listing_data.get("title"),
                "description": listing_data.get("description"),
                "imageUrls": listing_data.get("image_urls", []),
            },
        }
        await self._request("PUT", f"/sell/inventory/v1/inventory_item/{sku}", body=inventory_item)
        offer = {
            "sku": sku, "marketplaceId": "EBAY_US", "format": "FIXED_PRICE",
            "availableQuantity": listing_data.get("quantity", 1),
            "categoryId": listing_data.get("category_id", ""),
            "listingDescription": listing_data.get("description", ""),
            "pricingSummary": {"price": {"value": str(listing_data.get("price", 0)), "currency": "USD"}},
        }
        return await self._request("POST", "/sell/inventory/v1/offer", body=offer)

    async def publish_listing(self, listing_id: str) -> dict:
        from app.core.database import tenant_session
        from app.models.remaining_models import Listing
        from sqlalchemy import select
        async with tenant_session(self.tenant_slug) as db:
            result = await db.execute(select(Listing).where(Listing.id == listing_id))
            listing = result.scalar_one_or_none()
        if not listing:
            raise ValueError(f"Listing {listing_id} not found")
        return await self.create_listing({
            "title": listing.title, "description": listing.description,
            "price": float(listing.price or 0), "quantity": 10,
        })

    async def get_orders(self, filter_str: str = None) -> dict:
        params = {}
        if filter_str:
            params["filter"] = filter_str
        return await self._request("GET", "/sell/fulfillment/v1/order", params=params)
