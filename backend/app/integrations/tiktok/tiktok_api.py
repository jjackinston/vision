"""TikTok Shop API Integration."""
import httpx
import hmac
import hashlib
import time
from typing import Optional
from app.core.config import settings
from app.core.cache import cached, cache_get, cache_set

TIKTOK_BASE = "https://open-api.tiktokglobalshop.com"


class TikTokShopAPI:
    def __init__(self, access_token: str = None, shop_id: str = None, tenant_slug: str = None):
        self.access_token = access_token
        self.shop_id = shop_id
        self.tenant_slug = tenant_slug

    def _sign_request(self, path: str, params: dict, body: str = "") -> str:
        """Generate HMAC-SHA256 signature for TikTok Shop API."""
        ts = str(int(time.time()))
        sorted_params = "".join(f"{k}{v}" for k, v in sorted(params.items())
                                if k not in ("access_token", "sign"))
        sign_str = f"{settings.TIKTOK_APP_SECRET}{path}{sorted_params}{body}{ts}"
        return hmac.new(settings.TIKTOK_APP_SECRET.encode(), sign_str.encode(), hashlib.sha256).hexdigest()

    async def _request(self, method: str, path: str, params: dict = None, body: dict = None) -> dict:
        params = params or {}
        params.update({
            "app_key": settings.TIKTOK_APP_KEY,
            "access_token": self.access_token or "",
            "timestamp": str(int(time.time())),
            "shop_id": self.shop_id or "",
        })
        body_str = str(body) if body else ""
        params["sign"] = self._sign_request(path, params, body_str)
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.request(
                method, f"{TIKTOK_BASE}{path}",
                params=params, json=body
            )
            resp.raise_for_status()
            return resp.json()

    @cached(ttl=1800, key_prefix="tiktok_products")
    async def search_products(self, query: str, page_size: int = 20) -> dict:
        return await self._request("POST", "/api/products/search", body={
            "keyword": query, "page_size": min(page_size, 100), "page_number": 1
        })

    async def get_product(self, product_id: str) -> dict:
        return await self._request("GET", "/api/products/details", params={"product_id": product_id})

    async def create_product(self, product_data: dict) -> dict:
        return await self._request("POST", "/api/products", body=product_data)

    async def get_orders(self, order_status: str = "UNPAID") -> dict:
        return await self._request("POST", "/api/orders/search", body={"order_status": order_status})

    async def get_shop_info(self) -> dict:
        return await self._request("GET", "/api/shop/get_authorized_shop")

    async def get_categories(self) -> dict:
        return await self._request("GET", "/api/products/categories")

    async def get_live_analytics(self) -> dict:
        """Get live shopping stream analytics."""
        return await self._request("GET", "/api/live/analytics")

    async def publish_listing(self, listing_id: str) -> dict:
        from app.core.database import tenant_session
        from app.models.remaining_models import Listing
        from sqlalchemy import select
        async with tenant_session(self.tenant_slug) as db:
            result = await db.execute(select(Listing).where(Listing.id == listing_id))
            listing = result.scalar_one_or_none()
        if not listing:
            raise ValueError(f"Listing {listing_id} not found")
        return await self.create_product({
            "title": listing.title,
            "description": listing.description,
            "price": float(listing.price or 0),
            "status": "draft",
        })

    @staticmethod
    def get_oauth_url(state: str) -> str:
        return (f"https://auth.tiktok-shops.com/oauth/authorize?"
                f"app_key={settings.TIKTOK_APP_KEY}&state={state}")
