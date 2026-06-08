"""
Cross-process WebSocket event publisher.

Celery workers run in a separate process and cannot call the FastAPI
ConnectionManager directly.  This module lets any process publish a
WebSocket event to Redis; the FastAPI subscriber loop picks it up and
delivers it to connected clients.

Usage (from a Celery task or any sync/async context):
    from app.websocket.publisher import publish_ws_event
    await publish_ws_event(tenant_id, {"type": "agent_completed", ...})

    # Or from sync context:
    from app.websocket.publisher import publish_ws_event_sync
    publish_ws_event_sync(tenant_id, {"type": "inventory_alert", ...})

Channel naming: "ws_events:{tenant_id}"
Broadcast channel:  "ws_events:__all__"  (delivered to every connected tenant)
"""
import json
import logging
from typing import Any

logger = logging.getLogger(__name__)

# Redis channel prefix
_CHANNEL_PREFIX = "ws_events"


def _channel(tenant_id: str) -> str:
    return f"{_CHANNEL_PREFIX}:{tenant_id}"


async def publish_ws_event(tenant_id: str, event: dict[str, Any]) -> bool:
    """
    Publish a WebSocket event for a specific tenant.
    Returns True if published to Redis, False if Redis is unavailable
    (in which case the event is silently dropped — WS is best-effort).
    """
    from app.core.cache import get_redis
    r = await get_redis()
    if r is None:
        logger.debug("Redis unavailable — WS event dropped: %s", event.get("type"))
        return False
    try:
        payload = json.dumps(event, default=str)
        await r.publish(_channel(tenant_id), payload)
        return True
    except Exception as exc:
        logger.warning("Failed to publish WS event: %s", exc)
        return False


async def publish_ws_broadcast(event: dict[str, Any]) -> bool:
    """Publish an event that will be broadcast to ALL connected tenants."""
    return await publish_ws_event("__all__", event)


def publish_ws_event_sync(tenant_id: str, event: dict[str, Any]) -> None:
    """
    Sync wrapper — safe to call from a Celery task body (runs in asyncio loop).
    Uses the same asyncio event loop as the task's run_async() helper.
    """
    import asyncio
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(publish_ws_event(tenant_id, event))
    except Exception as exc:
        logger.warning("publish_ws_event_sync failed: %s", exc)
    finally:
        loop.close()


# ── Typed event helpers (keeps tasks clean) ──────────────────────────────────

async def publish_agent_completed(
    tenant_id: str,
    agent_name: str,
    run_id: str,
    findings_count: int = 0,
    summary: str = "",
) -> None:
    await publish_ws_event(tenant_id, {
        "type": "agent_completed",
        "agent": agent_name,
        "run_id": run_id,
        "status": "completed",
        "findings_count": findings_count,
        "summary": summary or f"{agent_name} found {findings_count} item(s)",
        "message": summary or f"Agent {agent_name} finished with {findings_count} finding(s)",
        "action_url": "/agents",
    })


async def publish_agent_failed(tenant_id: str, agent_name: str, run_id: str, error: str) -> None:
    await publish_ws_event(tenant_id, {
        "type": "agent_completed",
        "agent": agent_name,
        "run_id": run_id,
        "status": "failed",
        "findings_count": 0,
        "summary": f"Agent {agent_name} failed: {error[:100]}",
        "message": f"Agent {agent_name} failed",
        "action_url": "/agents",
    })


async def publish_inventory_alert(
    tenant_id: str,
    sku: str,
    product_name: str,
    days_remaining: int,
    qty_on_hand: int,
) -> None:
    severity = "critical" if days_remaining <= 7 else "warning"
    await publish_ws_event(tenant_id, {
        "type": "inventory_alert",
        "severity": severity,
        "sku": sku,
        "product_name": product_name,
        "days_remaining": days_remaining,
        "qty_on_hand": qty_on_hand,
        "message": f"Low stock: {product_name} — {days_remaining}d remaining ({qty_on_hand} units)",
        "action_url": "/inventory",
    })


async def publish_ppc_alert(
    tenant_id: str,
    campaign_name: str,
    acos_pct: float,
) -> None:
    await publish_ws_event(tenant_id, {
        "type": "ppc_alert",
        "campaign": campaign_name,
        "acos_pct": round(acos_pct, 1),
        "message": f"High ACoS: {campaign_name} at {acos_pct:.1f}%",
        "action_url": "/ppc",
    })


async def publish_trend_detected(
    tenant_id: str,
    topic: str,
    score: float,
    source: str,
) -> None:
    await publish_ws_event(tenant_id, {
        "type": "trend_detected",
        "topic": topic,
        "score": score,
        "source": source,
        "message": f"Trend: {topic} (score {score:.0f}) via {source}",
        "action_url": "/trends",
    })
