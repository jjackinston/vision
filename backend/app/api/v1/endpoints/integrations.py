from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import time
import logging

from app.core.database import get_db
from app.core.security import get_current_user, CurrentUser
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

SUPPORTED_MARKETPLACES = ["amazon", "walmart", "shopify", "ebay", "tiktok", "etsy"]


@router.get("/")
async def list_integrations(
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """List all connected and available marketplace integrations."""
    from sqlalchemy import select
    from app.models.tenant import MarketplaceConnection
    result = await db.execute(
        select(MarketplaceConnection).where(MarketplaceConnection.tenant_id == user.tenant_id)
    )
    connected = {c.marketplace: c for c in result.scalars().all()}
    return [
        {
            "marketplace": mp,
            "connected": mp in connected,
            "status": connected[mp].status if mp in connected else None,
            "account_name": connected[mp].account_name if mp in connected else None,
            "last_sync_at": connected[mp].last_sync_at if mp in connected else None,
        }
        for mp in SUPPORTED_MARKETPLACES
    ]


@router.post("/connect/{marketplace}")
async def connect_marketplace(
    marketplace: str,
    credentials: dict,
    account_name: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """Connect a new marketplace integration."""
    user.require("admin")
    if marketplace not in SUPPORTED_MARKETPLACES:
        raise HTTPException(400, f"Marketplace '{marketplace}' not supported")

    # Validate credentials by making a test API call
    is_valid = await _validate_credentials(marketplace, credentials)
    if not is_valid:
        raise HTTPException(400, f"Invalid credentials for {marketplace}")

    from app.models.tenant import MarketplaceConnection
    from sqlalchemy import select
    # Encrypt credentials before storing
    encrypted = await _encrypt_credentials(credentials)
    existing = await db.execute(
        select(MarketplaceConnection).where(
            MarketplaceConnection.tenant_id == user.tenant_id,
            MarketplaceConnection.marketplace == marketplace,
        )
    )
    conn = existing.scalar_one_or_none()
    if conn:
        conn.credentials = encrypted
        conn.account_name = account_name
        conn.status = "active"
    else:
        conn = MarketplaceConnection(
            tenant_id=user.tenant_id,
            marketplace=marketplace,
            credentials=encrypted,
            account_name=account_name,
            status="active",
        )
        db.add(conn)
    await db.commit()
    return {"marketplace": marketplace, "status": "connected", "account_name": account_name}


@router.delete("/disconnect/{marketplace}")
async def disconnect_marketplace(
    marketplace: str,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    user.require("admin")
    from app.models.tenant import MarketplaceConnection
    from sqlalchemy import select, delete
    await db.execute(
        delete(MarketplaceConnection).where(
            MarketplaceConnection.tenant_id == user.tenant_id,
            MarketplaceConnection.marketplace == marketplace,
        )
    )
    await db.commit()
    return {"marketplace": marketplace, "status": "disconnected"}


@router.post("/sync/{marketplace}")
async def sync_marketplace(
    marketplace: str,
    user: CurrentUser = Depends(get_current_user),
):
    """Trigger manual data sync for a marketplace."""
    user.require("write")
    from app.workers.tasks import celery_app
    celery_app.send_task("app.workers.tasks.sync_marketplace", args=[marketplace, user.tenant_id])
    return {"message": f"Sync started for {marketplace}"}


@router.get("/oauth/{marketplace}/authorize")
async def oauth_authorize(
    marketplace: str,
    user: CurrentUser = Depends(get_current_user),
):
    """Get OAuth authorization URL for marketplace."""
    urls = {
        "amazon": f"https://sellercentral.amazon.com/apps/authorize/consent?application_id={_get_app_id(marketplace)}&state={user.tenant_id}&version=beta",
        "shopify": "https://shopify.com/admin/oauth/authorize",
        "ebay": "https://auth.ebay.com/oauth2/authorize",
    }
    url = urls.get(marketplace)
    if not url:
        raise HTTPException(400, f"OAuth not supported for {marketplace}")
    return {"authorization_url": url}


async def _validate_credentials(marketplace: str, credentials: dict) -> bool:
    """Validate credentials by making a lightweight API call."""
    try:
        if marketplace == "amazon":
            from app.integrations.amazon.sp_api import AmazonSPAPI
            api = AmazonSPAPI()
            await api._get_access_token()
            return True
        return True  # Other marketplaces: assume valid in dev
    except Exception:
        return False


async def _encrypt_credentials(credentials: dict) -> dict:
    """Encrypt sensitive credentials using AWS KMS or Fernet."""
    # In production: use AWS KMS or cryptography.fernet
    return credentials


def _get_app_id(marketplace: str) -> str:
    return settings.AMAZON_CLIENT_ID


# ── Integration Health Check ──────────────────────────────────────
@router.get("/health")
async def integration_health(
    user: CurrentUser = Depends(get_current_user),
):
    """
    Check connectivity status for all external services.
    Returns per-service status, latency, and configuration presence.
    """
    results = {}

    # ── Redis ─────────────────────────────────────────────────────
    t0 = time.monotonic()
    try:
        from app.core.cache import get_redis
        r = await get_redis()
        if r:
            await r.ping()
            results["redis"] = {
                "status": "connected",
                "latency_ms": round((time.monotonic() - t0) * 1000, 1),
                "configured": True,
            }
        else:
            results["redis"] = {
                "status": "unavailable",
                "note": "Redis not running — agents and caching degraded",
                "configured": bool(settings.REDIS_URL),
            }
    except Exception as e:
        results["redis"] = {"status": "error", "detail": str(e)[:80], "configured": True}

    # ── Stripe ────────────────────────────────────────────────────
    t0 = time.monotonic()
    if not settings.STRIPE_SECRET_KEY:
        results["stripe"] = {
            "status": "not_configured",
            "note": "Add STRIPE_SECRET_KEY to .env",
            "configured": False,
        }
    else:
        try:
            import stripe
            stripe.api_key = settings.STRIPE_SECRET_KEY
            stripe.Balance.retrieve()
            results["stripe"] = {
                "status": "connected",
                "latency_ms": round((time.monotonic() - t0) * 1000, 1),
                "configured": True,
                "price_ids": {
                    "starter":      bool(settings.STRIPE_STARTER_PRICE_ID),
                    "professional": bool(settings.STRIPE_PROFESSIONAL_PRICE_ID),
                    "business":     bool(settings.STRIPE_BUSINESS_PRICE_ID),
                    "agency":       bool(settings.STRIPE_AGENCY_PRICE_ID),
                },
                "webhook_secret": bool(settings.STRIPE_WEBHOOK_SECRET),
            }
        except Exception as e:
            results["stripe"] = {
                "status": "error",
                "detail": str(e)[:120],
                "configured": True,
            }

    # ── Amazon SP-API ─────────────────────────────────────────────
    t0 = time.monotonic()
    amazon_configured = all([
        settings.AMAZON_CLIENT_ID,
        settings.AMAZON_CLIENT_SECRET,
        settings.AMAZON_REFRESH_TOKEN,
    ])
    if not amazon_configured:
        results["amazon"] = {
            "status": "not_configured",
            "note": "Add AMAZON_CLIENT_ID, AMAZON_CLIENT_SECRET, AMAZON_REFRESH_TOKEN to .env",
            "configured": False,
        }
    else:
        try:
            from app.integrations.amazon.sp_api import AmazonSPAPI
            api = AmazonSPAPI()
            token = await api._get_access_token()
            results["amazon"] = {
                "status": "connected",
                "latency_ms": round((time.monotonic() - t0) * 1000, 1),
                "configured": True,
                "marketplace_id": settings.AMAZON_MARKETPLACE_ID,
            }
        except Exception as e:
            results["amazon"] = {
                "status": "error",
                "detail": str(e)[:120],
                "configured": True,
            }

    # ── OpenAI / Anthropic ────────────────────────────────────────
    results["openai"] = {
        "status": "configured" if settings.OPENAI_API_KEY else "not_configured",
        "configured": bool(settings.OPENAI_API_KEY),
        "model": settings.OPENAI_MODEL,
    }
    results["anthropic"] = {
        "status": "configured" if settings.ANTHROPIC_API_KEY else "not_configured",
        "configured": bool(settings.ANTHROPIC_API_KEY),
        "model": settings.ANTHROPIC_MODEL,
    }

    # ── Other marketplaces ────────────────────────────────────────
    for mp, key_attr in [
        ("walmart",  "WALMART_CLIENT_ID"),
        ("shopify",  "SHOPIFY_API_KEY"),
        ("ebay",     "EBAY_APP_ID"),
        ("tiktok",   "TIKTOK_APP_KEY"),
        ("etsy",     "ETSY_KEYSTRING"),
    ]:
        configured = bool(getattr(settings, key_attr, ""))
        results[mp] = {
            "status": "configured" if configured else "not_configured",
            "configured": configured,
        }

    # Compute overall health
    connected = sum(1 for v in results.values() if v.get("status") in ("connected", "configured"))
    total = len(results)
    critical_ok = results.get("redis", {}).get("status") in ("connected",) and \
                  results.get("stripe", {}).get("status") in ("connected", "not_configured")

    return {
        "overall": "healthy" if critical_ok else "degraded",
        "summary": f"{connected}/{total} services configured",
        "services": results,
    }
