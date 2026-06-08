"""Etsy Open API v3 Integration."""
import httpx
from app.core.config import settings
from app.core.cache import cached, cache_get, cache_set

ETSY_BASE = "https://openapi.etsy.com/v3"


class EtsyAPI:
    def __init__(self, access_token: str = None, shop_id: str = None, tenant_slug: str = None):
        self.access_token = access_token
        self.shop_id = shop_id
        self.tenant_slug = tenant_slug

    def _headers(self) -> dict:
        h = {"x-api-key": settings.ETSY_KEYSTRING, "Content-Type": "application/json"}
        if self.access_token:
            h["Authorization"] = f"Bearer {self.access_token}"
        return h

    async def _request(self, method: str, path: str, params: dict = None, body: dict = None) -> dict:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.request(
                method, f"{ETSY_BASE}{path}",
                headers=self._headers(), params=params, json=body
            )
            resp.raise_for_status()
            return resp.json()

    @cached(ttl=1800, key_prefix="etsy_search")
    async def search_listings(self, query: str, limit: int = 25, taxonomy_id: int = None) -> dict:
        params = {"keywords": query, "limit": min(limit, 100), "sort_on": "score"}
        if taxonomy_id:
            params["taxonomy_id"] = taxonomy_id
        return await self._request("GET", "/application/listings/active", params=params)

    async def get_listing(self, listing_id: str) -> dict:
        return await self._request("GET", f"/application/listings/{listing_id}")

    async def get_shop_listings(self, limit: int = 25, offset: int = 0) -> dict:
        return await self._request("GET", f"/application/shops/{self.shop_id}/listings/active",
                                    params={"limit": limit, "offset": offset})

    async def create_draft_listing(self, listing_data: dict) -> dict:
        return await self._request("POST", f"/application/shops/{self.shop_id}/listings", body={
            "quantity": listing_data.get("quantity", 10),
            "title": listing_data.get("title", ""),
            "description": listing_data.get("description", ""),
            "price": listing_data.get("price", 0),
            "who_made": listing_data.get("who_made", "i_did"),
            "when_made": listing_data.get("when_made", "2020_2024"),
            "taxonomy_id": listing_data.get("taxonomy_id", 0),
            "tags": listing_data.get("tags", [])[:13],
            "materials": listing_data.get("materials", []),
            "type": "physical",
        })

    async def get_shop_receipts(self, min_created: int = None) -> dict:
        params = {}
        if min_created:
            params["min_created"] = min_created
        return await self._request("GET", f"/application/shops/{self.shop_id}/receipts", params=params)

    async def get_shop_stats(self) -> dict:
        return await self._request("GET", f"/application/shops/{self.shop_id}/stats")

    async def get_taxonomy(self) -> dict:
        return await self._request("GET", "/application/seller-taxonomy/nodes")

    async def publish_listing(self, listing_id: str) -> dict:
        from app.core.database import tenant_session
        from app.models.remaining_models import Listing
        from sqlalchemy import select
        async with tenant_session(self.tenant_slug) as db:
            result = await db.execute(select(Listing).where(Listing.id == listing_id))
            listing = result.scalar_one_or_none()
        if not listing:
            raise ValueError(f"Listing {listing_id} not found")
        tags = listing.backend_keywords[:13] if listing.backend_keywords else []
        return await self.create_draft_listing({
            "title": listing.title, "description": listing.description,
            "price": float(listing.price or 0), "tags": tags,
        })

    @staticmethod
    def get_oauth_url(state: str, redirect_uri: str) -> str:
        import hashlib, secrets
        code_verifier = secrets.token_urlsafe(43)
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).rstrip(b"=").decode()
        scope = "listings_r listings_w shops_r shops_w transactions_r"
        return (f"https://www.etsy.com/oauth/connect?response_type=code"
                f"&redirect_uri={redirect_uri}&scope={scope}&client_id={settings.ETSY_KEYSTRING}"
                f"&state={state}&code_challenge={code_challenge}&code_challenge_method=S256")
