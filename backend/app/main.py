from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import select, func
import logging
import time
import uuid
import asyncio
import json
from datetime import datetime, timedelta

from app.core.config import settings
from app.core.cache import rate_limiter
from app.api.v1.router import api_router
from app.websocket.router import router as ws_router
from app.websocket.manager import manager


# ── Structured JSON logging (production) / human-readable (dev) ──────────────
class _JSONFormatter(logging.Formatter):
    """Emit each log record as a single JSON line — friendly to Datadog / CloudWatch."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S.%fZ"),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        # Forward any extra fields attached via LoggerAdapter / extra={}
        for key in ("request_id", "tenant_id", "user_id", "path", "method", "status", "ms"):
            if hasattr(record, key):
                payload[key] = getattr(record, key)
        return json.dumps(payload, default=str)


def _configure_logging() -> None:
    root = logging.getLogger()
    root.handlers.clear()
    handler = logging.StreamHandler()
    if settings.is_production:
        handler.setFormatter(_JSONFormatter())
    else:
        handler.setFormatter(
            logging.Formatter("%(asctime)s  %(levelname)-8s  %(name)s  %(message)s")
        )
    root.addHandler(handler)
    root.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    # Suppress noisy third-party loggers
    for noisy in ("httpx", "httpcore", "stripe", "multipart"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


_configure_logging()
logger = logging.getLogger(__name__)


def _client_ip(request: Request) -> str:
    """
    Extract the real client IP.
    When running behind nginx (or any proxy), trust X-Real-IP first,
    then X-Forwarded-For, then fall back to the direct connection IP.
    """
    x_real_ip = request.headers.get("X-Real-IP")
    if x_real_ip:
        return x_real_ip.strip()
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # leftmost entry is the original client
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else "unknown"

_stockout_task: asyncio.Task | None = None
_ws_subscriber_task: asyncio.Task | None = None


async def _stockout_alert_loop():
    """
    Background task: every 5 minutes query inventory for near-stockout items
    and push real-time WebSocket alerts to all affected tenants.
    """
    from app.core.database import AsyncSessionLocal
    from app.websocket.manager import push_inventory_alert
    from sqlalchemy import text

    while True:
        try:
            async with AsyncSessionLocal() as db:
                cutoff = datetime.utcnow() + timedelta(days=14)
                result = await db.execute(
                    text(
                        """
                        SELECT
                            i.sku,
                            COALESCE(p.title, i.sku) AS product_name,
                            EXTRACT(DAY FROM (i.stockout_date - NOW()))::int AS days_remaining,
                            i.quantity_on_hand
                        FROM inventory i
                        LEFT JOIN products p ON p.id = i.product_id
                        WHERE i.stockout_date IS NOT NULL
                          AND i.stockout_date <= :cutoff
                          AND i.quantity_on_hand > 0
                        ORDER BY i.stockout_date ASC
                        LIMIT 50
                        """
                    ),
                    {"cutoff": cutoff},
                )
                rows = result.fetchall()

            # Broadcast to all currently-connected tenants
            # (inventory has no tenant_id column — multi-tenant isolation handled at auth layer)
            for row in rows:
                sku, product_name, days_remaining, qty = row
                days_remaining = max(int(days_remaining or 0), 0)
                payload = {
                    "type": "inventory_alert",
                    "severity": "critical" if days_remaining <= 7 else "warning",
                    "sku": str(sku),
                    "product_name": str(product_name),
                    "days_remaining": days_remaining,
                    "qty_on_hand": int(qty or 0),
                    "message": f"Low stock: {product_name} — {days_remaining}d remaining ({qty} units)",
                    "action_url": "/inventory",
                }
                await manager.broadcast_all(payload)

            if rows:
                logger.info(f"[stockout-loop] Pushed alerts for {len(rows)} near-stockout SKU(s)")

        except asyncio.CancelledError:
            break
        except Exception as exc:
            logger.warning(f"[stockout-loop] Error: {exc}")

        await asyncio.sleep(300)  # 5 minutes


async def _ws_redis_subscriber():
    """
    Subscribe to Redis pub/sub channels published by Celery workers.
    Pattern: ws_events:{tenant_id}  (or ws_events:__all__ for broadcasts)
    Relays messages to the in-process WebSocket ConnectionManager.

    Gracefully exits when Redis is unavailable and retries every 30s.
    """
    import json as _json
    from app.core.cache import get_redis

    while True:
        try:
            r = await get_redis()
            if r is None:
                await asyncio.sleep(30)
                continue

            # Need a fresh connection for pubsub (can't reuse command connection)
            from app.core.config import settings as _settings
            import redis.asyncio as _aioredis
            pubsub_conn = _aioredis.from_url(
                _settings.REDIS_URL, decode_responses=True, socket_connect_timeout=3
            )
            pubsub = pubsub_conn.pubsub()
            await pubsub.psubscribe("ws_events:*")
            logger.info("[ws-subscriber] Subscribed to ws_events:* on Redis")

            async for raw in pubsub.listen():
                if raw["type"] != "pmessage":
                    continue
                channel: str = raw.get("channel", "")
                tenant_id = channel.removeprefix("ws_events:")
                try:
                    event = _json.loads(raw["data"])
                except Exception:
                    continue
                if tenant_id == "__all__":
                    await manager.broadcast_all(event)
                else:
                    await manager.broadcast_to_tenant(tenant_id, event)

        except asyncio.CancelledError:
            logger.info("[ws-subscriber] Shutting down")
            break
        except Exception as exc:
            logger.warning("[ws-subscriber] Error: %s — retrying in 30s", exc)
            await asyncio.sleep(30)


async def _ensure_plans_seeded():
    """
    Ensure subscription plans exist in the database.
    Runs at startup — lightweight (single SELECT then bulk INSERT if empty).
    Safe to run against a production DB: only inserts if plans table is empty.
    """
    from app.core.database import AsyncSessionLocal
    from app.models.tenant import Plan
    from decimal import Decimal
    from sqlalchemy import func

    PLANS = [
        {"name": "Starter",      "price_monthly": Decimal("49.00"),  "price_annual": Decimal("470.00"),  "limits": {"products": 50,   "keywords": 500,   "api_calls": 10000,  "users": 1,  "marketplaces": 2, "agents": 2}, "features": {"ai_analysis": True,  "competitor_tracking": False, "ppc_automation": False, "api_access": False, "white_label": False}},
        {"name": "Professional", "price_monthly": Decimal("149.00"), "price_annual": Decimal("1430.00"), "limits": {"products": 100,  "keywords": 5000,  "api_calls": 100000, "users": 3,  "marketplaces": 4, "agents": 5}, "features": {"ai_analysis": True,  "competitor_tracking": True,  "ppc_automation": True,  "api_access": False, "white_label": False}},
        {"name": "Business",     "price_monthly": Decimal("299.00"), "price_annual": Decimal("2870.00"), "limits": {"products": 500,  "keywords": 25000, "api_calls": 500000, "users": 10, "marketplaces": 6, "agents": 7}, "features": {"ai_analysis": True,  "competitor_tracking": True,  "ppc_automation": True,  "api_access": True,  "white_label": False}},
        {"name": "Agency",       "price_monthly": Decimal("599.00"), "price_annual": Decimal("5750.00"), "limits": {"products": -1,   "keywords": -1,    "api_calls": -1,     "users": 25, "marketplaces": 6, "agents": 7}, "features": {"ai_analysis": True,  "competitor_tracking": True,  "ppc_automation": True,  "api_access": True,  "white_label": True}},
    ]

    try:
        async with AsyncSessionLocal() as db:
            count = await db.scalar(select(func.count()).select_from(Plan))
            if count and count >= 4:
                logger.debug("Plans already seeded (%d rows)", count)
                return
            for p in PLANS:
                existing = await db.scalar(select(Plan).where(Plan.name == p["name"]))
                if not existing:
                    db.add(Plan(is_active=True, **p))
            await db.commit()
            logger.info("Plans seeded successfully")
    except Exception as exc:
        logger.warning("Could not seed plans (non-fatal): %s", exc)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _stockout_task, _ws_subscriber_task
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    await _ensure_plans_seeded()
    _stockout_task = asyncio.create_task(_stockout_alert_loop())
    _ws_subscriber_task = asyncio.create_task(_ws_redis_subscriber())
    yield
    for task in (_stockout_task, _ws_subscriber_task):
        if task and not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
    logger.info("Shutting down")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Powered Multi-Platform E-Commerce Intelligence Platform",
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
    lifespan=lifespan,
    debug=not settings.is_production,  # expose tracebacks in dev
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request.state.request_id = request_id
    start_time = time.time()
    response = await call_next(request)
    duration = (time.time() - start_time) * 1000
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Response-Time"] = f"{duration:.2f}ms"

    # Structured access log (skip health-check noise in production)
    path = request.url.path
    if not (settings.is_production and path in ("/health", "/metrics")):
        logger.info(
            "%s %s %s %.0fms",
            request.method, path, response.status_code, duration,
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": path,
                "status": response.status_code,
                "ms": round(duration, 1),
                "ip": _client_ip(request),
            },
        )
    return response


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Skip rate limiting for health checks and static assets
    path = request.url.path
    if path in ("/health", "/metrics") or path.startswith("/_next/"):
        return await call_next(request)

    # Use real client IP (works correctly behind nginx proxy)
    ip = _client_ip(request)
    key = f"rate_limit:{ip}"
    allowed, remaining = await rate_limiter.is_allowed(key, settings.RATE_LIMIT_PER_MINUTE, 60)
    if not allowed:
        logger.warning(
            "Rate limit exceeded for %s on %s", ip, path,
            extra={"ip": ip, "path": path},
        )
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded. Please try again later."},
            headers={"X-RateLimit-Remaining": "0", "Retry-After": "60"},
        )
    response = await call_next(request)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    return response


# Routes
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(ws_router)  # WebSocket at /ws/{tenant_id}


@app.get("/health")
async def health_check():
    """Production health check — verifies DB and Redis connectivity."""
    import time
    checks: dict = {}
    overall = "healthy"

    # Database
    try:
        from app.core.database import AsyncSessionLocal
        from sqlalchemy import text
        t0 = time.monotonic()
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        checks["database"] = {"status": "ok", "latency_ms": round((time.monotonic() - t0) * 1000, 1)}
    except Exception as exc:
        checks["database"] = {"status": "error", "detail": str(exc)[:80]}
        overall = "degraded"

    # Redis (optional — degrades gracefully)
    try:
        from app.core.cache import get_redis
        t0 = time.monotonic()
        r = await get_redis()
        if r:
            await r.ping()
            checks["redis"] = {"status": "ok", "latency_ms": round((time.monotonic() - t0) * 1000, 1)}
        else:
            checks["redis"] = {"status": "unavailable"}
    except Exception as exc:
        checks["redis"] = {"status": "error", "detail": str(exc)[:80]}

    status_code = 200 if overall == "healthy" else 503
    return JSONResponse(
        status_code=status_code,
        content={"status": overall, "version": settings.APP_VERSION, "checks": checks},
    )


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "The Bloomberg Terminal + Salesforce + ChatGPT for E-Commerce",
    }
