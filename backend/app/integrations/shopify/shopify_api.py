"""
Shopify Admin API Integration
Uses Shopify Admin REST API 2024-04
"""
import httpx
from typing import Optional
from app.core.cache import cached, cache_get, cache_set

SHOPIFY_API_VERSION = "2024-04"


class ShopifyAPI:
    def __init__(self, shop_domain: str = None, access_token: str = None, tenant_slug: str = None):
        self.shop_domain = shop_domain
        self.access_token = access_token
        self.tenant_slug = tenant_slug

    def _base_url(self) -> str:
        return f"https://{self.shop_domain}/admin/api/{SHOPIFY_API_VERSION}"

    def _headers(self) -> dict:
        return {
            "X-Shopify-Access-Token": self.access_token,
            "Content-Type": "application/json",
        }

    async def _load_credentials(self) -> None:
        """Load stored credentials for this tenant's Shopify connection."""
        if self.access_token:
            return
        cache_key = f"shopify_creds:{self.tenant_slug}"
        creds = await cache_get(cache_key)
        if creds:
            self.shop_domain = creds["shop_domain"]
            self.access_token = creds["access_token"]

    async def _request(self, method: str, path: str, params: dict = None, body: dict = None) -> dict:
        await self._load_credentials()
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.request(
                method, f"{self._base_url()}{path}",
                headers=self._headers(), params=params, json=body
            )
            resp.raise_for_status()
            return resp.json()

    @cached(ttl=1800, key_prefix="shopify_products")
    async def get_products(self, limit: int = 50, page_info: str = None) -> dict:
        params = {"limit": min(limit, 250)}
        if page_info:
            params["page_info"] = page_info
        return await self._request("GET", "/products.json", params=params)

    async def get_product(self, product_id: str) -> dict:
        return await self._request("GET", f"/products/{product_id}.json")

    async def create_product(self, product_data: dict) -> dict:
        return await self._request("POST", "/products.json", body={"product": product_data})

    async def update_product(self, product_id: str, updates: dict) -> dict:
        return await self._request("PUT", f"/products/{product_id}.json", body={"product": updates})

    async def get_orders(self, status: str = "open", limit: int = 50) -> dict:
        return await self._request("GET", "/orders.json", params={"status": status, "limit": limit})

    async def get_inventory_levels(self, location_id: str = None) -> dict:
        params = {}
        if location_id:
            params["location_ids[]"] = location_id
        return await self._request("GET", "/inventory_levels.json", params=params)

    async def update_inventory(self, inventory_item_id: str, location_id: str, available: int) -> dict:
        return await self._request("POST", "/inventory_levels/set.json", body={
            "location_id": location_id,
            "inventory_item_id": inventory_item_id,
            "available": available,
        })

    async def get_analytics(self, since: str, until: str) -> dict:
        return await self._request("GET", "/reports.json")

    async def publish_listing(self, listing_id: str) -> dict:
        from app.core.database import tenant_session
        from app.models.remaining_models import Listing
        from sqlalchemy import select
        async with tenant_session(self.tenant_slug) as db:
            result = await db.execute(select(Listing).where(Listing.id == listing_id))
            listing = result.scalar_one_or_none()
        if not listing:
            raise ValueError(f"Listing {listing_id} not found")
        product_data = {
            "title": listing.title,
            "body_html": f"<p>{listing.description or ''}</p>",
            "variants": [{"price": str(listing.price or 0), "inventory_management": "shopify"}],
        }
        if listing.images:
            product_data["images"] = [{"src": img} for img in (listing.images or [])]
        result = await self.create_product(product_data)
        return {"shopify_product_id": result["product"]["id"], "status": "published"}

    @staticmethod
    def get_oauth_url(shop: str, scopes: list, redirect_uri: str, state: str) -> str:
        from app.core.config import settings
        scope_str = ",".join(scopes)
        return (f"https://{shop}/admin/oauth/authorize?"
                f"client_id={settings.SHOPIFY_API_KEY}&scope={scope_str}"
                f"&redirect_uri={redirect_uri}&state={state}")

    @staticmethod
    async def exchange_code_for_token(shop: str, code: str) -> str:
        from app.core.config import settings
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"https://{shop}/admin/oauth/access_token", json={
                "client_id": settings.SHOPIFY_API_KEY,
                "client_secret": settings.SHOPIFY_API_SECRET,
                "code": code,
            })
            resp.raise_for_status()
            return resp.json()["access_token"]
