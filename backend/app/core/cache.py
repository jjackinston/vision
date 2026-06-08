"""
Redis cache layer for SellerVision AI.

Key namespacing:
    sv:<tenant_slug>:<domain>:<discriminator>

All helpers fail-open: if Redis is unavailable, queries hit the DB normally.
The `_redis_unavailable` flag prevents per-request reconnect attempts after
the first failure; it resets on the next worker restart.
"""
import json
import hashlib
import logging
from typing import Any, Optional, Callable
from functools import wraps
import redis.asyncio as aioredis

from app.core.config import settings

logger = logging.getLogger(__name__)

_redis: Optional[aioredis.Redis] = None
_redis_unavailable: bool = False  # set True after first failed connect


# ── Connection ─────────────────────────────────────────────────────────

async def get_redis() -> Optional[aioredis.Redis]:
    global _redis, _redis_unavailable
    if _redis_unavailable:
        return None
    if _redis is None:
        try:
            r = await aioredis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=1,
                socket_timeout=1,
            )
            await r.ping()
            _redis = r
            logger.info("Redis connected: %s", settings.REDIS_URL.split("@")[-1])
        except Exception as exc:
            logger.warning("Redis unavailable (%s) — caching disabled for this worker", exc)
            _redis_unavailable = True
            return None
    return _redis


# ── Low-level ops ──────────────────────────────────────────────────────

async def cache_get(key: str) -> Optional[Any]:
    r = await get_redis()
    if r is None:
        return None
    try:
        value = await r.get(key)
        return json.loads(value) if value else None
    except Exception:
        return None


async def cache_set(key: str, value: Any, ttl: int = settings.REDIS_CACHE_TTL) -> None:
    r = await get_redis()
    if r is None:
        return
    try:
        await r.setex(key, ttl, json.dumps(value, default=str))
    except Exception:
        pass


async def cache_delete(key: str) -> None:
    r = await get_redis()
    if r is None:
        return
    try:
        await r.delete(key)
    except Exception:
        pass


async def cache_delete_pattern(pattern: str) -> None:
    """Delete all keys matching a glob pattern. Uses SCAN to avoid blocking."""
    r = await get_redis()
    if r is None:
        return
    try:
        keys: list[str] = []
        async for key in r.scan_iter(match=pattern, count=100):
            keys.append(key)
        if keys:
            await r.delete(*keys)
    except Exception:
        pass


# ── Tenant-scoped helpers ──────────────────────────────────────────────

def make_cache_key(tenant_slug: str, domain: str, *parts: Any) -> str:
    """Build a deterministic, tenant-scoped cache key.

    Example:
        make_cache_key("acme", "analytics:overview", "30d", "amazon")
        → "sv:acme:analytics:overview:30d:amazon"
    """
    segments = [str(p) for p in parts if p is not None]
    return f"sv:{tenant_slug}:{domain}:{':'.join(segments)}" if segments else f"sv:{tenant_slug}:{domain}"


async def invalidate_tenant_cache(tenant_slug: str, domain: str = "") -> None:
    """Bust all cache keys for a tenant, optionally filtered to a domain prefix.

    Examples:
        await invalidate_tenant_cache("acme")           # nuke everything
        await invalidate_tenant_cache("acme", "products")  # only products
    """
    pattern = f"sv:{tenant_slug}:{domain}*"
    await cache_delete_pattern(pattern)


# ── Decorator ─────────────────────────────────────────────────────────

def cached(ttl: int = 3600, key_prefix: str = ""):
    """Decorator for caching async function results.

    ⚠  This only works reliably for *module-level* functions or static methods
    where args are serialisable. For service methods that receive a DB session
    as ``self``, use ``make_cache_key`` + ``cache_get``/``cache_set`` directly
    (the session object is not stable and would poison the key).
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Skip the first arg if it looks like a class instance (has __dict__)
            # so we don't hash an unstable session object
            hashable_args = tuple(
                a for a in args if not (hasattr(a, "__dict__") and not isinstance(a, (str, bytes, int, float)))
            )
            key_body = hashlib.md5(
                str(hashable_args).encode() + str(sorted(kwargs.items())).encode()
            ).hexdigest()
            prefix = key_prefix or func.__module__
            cache_key = f"{prefix}:{func.__name__}:{key_body}"
            cached_value = await cache_get(cache_key)
            if cached_value is not None:
                return cached_value
            result = await func(*args, **kwargs)
            if result is not None:
                await cache_set(cache_key, result, ttl)
            return result
        return wrapper
    return decorator


# ── Rate limiter ───────────────────────────────────────────────────────

class RateLimiter:
    """Sliding-window rate limiter using a Redis sorted set. Fails open."""

    async def is_allowed(self, key: str, limit: int, window_seconds: int) -> tuple[bool, int]:
        r = await get_redis()
        if r is None:
            return True, limit
        try:
            import time
            pipe = r.pipeline()
            now = time.time()
            window_start = now - window_seconds
            pipe.zremrangebyscore(key, 0, window_start)
            pipe.zadd(key, {str(now): now})
            pipe.zcard(key)
            pipe.expire(key, window_seconds)
            results = await pipe.execute()
            count = int(results[2])
            remaining = max(0, limit - count)
            return count <= limit, remaining
        except Exception:
            return True, limit


rate_limiter = RateLimiter()
