"""WebSocket endpoints for real-time dashboard updates."""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.websocket.manager import (
    manager,
    push_stockout_alert,
    push_opportunity_found,
    push_agent_started,
    push_agent_completed,
    push_price_alert,
    push_trend_detected,
    push_inventory_alert,
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.websocket("/ws/{tenant_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    tenant_id: str,
    token: str = Query(None),
):
    """
    Main WebSocket endpoint.
    Connect: ws://api.sellervisionai.com/ws/{tenant_id}?token=<clerk_jwt>
    Receives: JSON events of various types
    """
    # In production: validate token before connecting
    # if not await verify_ws_token(token, tenant_id):
    #     await websocket.close(code=1008)
    #     return

    await manager.connect(websocket, tenant_id)
    try:
        while True:
            # Handle client messages (heartbeat, subscriptions)
            data = await websocket.receive_text()
            import json
            try:
                msg = json.loads(data)
                if msg.get("type") == "ping":
                    await manager.send_personal(websocket, {"type": "pong"})
                elif msg.get("type") == "subscribe":
                    # Future: topic-based subscriptions
                    channels = msg.get("channels", [])
                    await manager.send_personal(websocket, {
                        "type": "subscribed",
                        "channels": channels,
                    })
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info(f"Client disconnected: tenant={tenant_id}")


# ── Test / demo event endpoints ───────────────────────────────────────────────

@router.post("/ws/test/{tenant_id}")
async def emit_test_event(tenant_id: str, event_type: str = "stockout_alert"):
    """
    Dev-only: emit a test WebSocket event to a tenant so the frontend can be
    verified without waiting for real data.

    Example:
        POST /ws/test/11111111-1111-1111-1111-111111111111?event_type=stockout_alert
    """
    handlers = {
        "stockout_alert": lambda: push_stockout_alert(tenant_id, "Widget A", 8),
        "opportunity_found": lambda: push_opportunity_found(tenant_id, "Ergonomic Desk Lamp", 87.3),
        "agent_started": lambda: push_agent_started(tenant_id, "Product Research Agent", "test-run-001", "Weekly product scan"),
        "agent_completed": lambda: push_agent_completed(tenant_id, "Product Research Agent", "test-run-001", findings_count=12, summary="Found 12 new opportunities"),
        "price_alert": lambda: push_price_alert(tenant_id, "Brand X", "B08XYZ", 24.99, 19.99),
        "trend_detected": lambda: push_trend_detected(tenant_id, "Portable Blenders", 91.0, "Google Trends"),
        "inventory_alert": lambda: push_inventory_alert(tenant_id, "SKU-007", "Widget B", 5, 42),
    }

    handler = handlers.get(event_type)
    if not handler:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=f"Unknown event_type. Choose: {list(handlers)}")

    await handler()
    active = manager.get_connection_count(tenant_id)
    return {"ok": True, "event_type": event_type, "tenant_id": tenant_id, "active_connections": active}
