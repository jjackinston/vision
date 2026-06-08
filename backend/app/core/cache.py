import json
import hashlib
import logging
from typing import Any, Optional, Callable
from functools import wraps
import redis.asyncio as aioredis

from app.core.config import settings

logger = logging.getLogger(__name__)

_redis: Optional[aioredis.Redis] = None
_redis_unavailable: bool = False  # set True after first failed connect; avoids per-request retries


async def get_redis() -> Optional[aioredis.Redis]:
    global _redis, _redis_unavailable
    if _redis_unavailable:
        return None
    if _redis is None:
        try:
            r = await aioredis.from_url(settings.REDIS_URL, decode_responses=True, socket_connect_timeout=1)
            await r.ping()
            _redis = r
        except Exception:
            logger.warning("Redis unavailable — caching disabled")
            _redis_unavailable = True
            return None
    return _redis


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
    r = await get_redis()
    if r is None:
        return
    try:
        keys = await r.keys(pattern)
        if keys:
            await r.delete(*keys)
    except Exception:
        pass


def cached(ttl: int = 3600, key_prefix: str = ""):
    """Decorator for caching async function results."""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{key_prefix}:{func.__name__}:{hashlib.md5(str(args).encode() + str(kwargs).encode()).hexdigest()}"
            cached_value = await cache_get(cache_key)
            if cached_value is not None:
                return cached_value
            result = await func(*args, **kwargs)
            await cache_set(cache_key, result, ttl)
            return result
        return wrapper
    return decorator


class RateLimiter:
    """Sliding window rate limiter using Redis. Fails open when Redis is unavailable."""

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
            count = results[2]
            remaining = max(0, limit - count)
            return count <= limit, remaining
        except Exception:
            return True, limit


rate_limiter = RateLimiter()
