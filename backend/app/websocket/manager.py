"""
WebSocket connection manager for real-time dashboard updates.
Pushes live events: stockout alerts, opportunity detections, agent results,
price changes, new trend detections.
"""
import json
import asyncio
from typing import Dict, Set, Optional, Any
from fastapi import WebSocket, WebSocketDisconnect, status
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Multi-tenant WebSocket manager.
    Connections are grouped by tenant_id for efficient broadcasting.
    """

    def __init__(self):
        # tenant_id → set of active WebSocket connections
        self._connections: Dict[str, Set[WebSocket]] = {}
        # websocket → tenant_id (reverse lookup for cleanup)
        self._tenant_map: Dict[WebSocket, str] = {}

    async def connect(self, websocket: WebSocket, tenant_id: str) -> None:
        await websocket.accept()
        if tenant_id not in self._connections:
            self._connections[tenant_id] = set()
        self._connections[tenant_id].add(websocket)
        self._tenant_map[websocket] = tenant_id
        logger.info(f"WebSocket connected: tenant={tenant_id}, total_connections={len(self._tenant_map)}")
        await self.send_personal(websocket, {"type": "connected", "tenant_id": tenant_id})

    def disconnect(self, websocket: WebSocket) -> None:
        tenant_id = self._tenant_map.pop(websocket, None)
        if tenant_id and tenant_id in self._connections:
            self._connections[tenant_id].discard(websocket)
            if not self._connections[tenant_id]:
                del self._connections[tenant_id]
        logger.info(f"WebSocket disconnected: tenant={tenant_id}")

    async def send_personal(self, websocket: WebSocket, message: Any) -> None:
        try:
            await websocket.send_text(json.dumps(message, default=str))
        except Exception as e:
            logger.warning(f"Failed to send personal message: {e}")
            self.disconnect(websocket)

    async def broadcast_to_tenant(self, tenant_id: str, message: Any) -> int:
        """Broadcast message to all connections for a tenant. Returns # sent."""
        connections = self._connections.get(tenant_id, set()).copy()
        if not connections:
            return 0
        sent = 0
        dead = set()
        payload = json.dumps(message, default=str)
        for ws in connections:
            try:
                await ws.send_text(payload)
                sent += 1
            except Exception:
                dead.add(ws)
        for ws in dead:
            self.disconnect(ws)
        return sent

    async def broadcast_all(self, message: Any) -> None:
        """Broadcast to all connected clients (use sparingly — system-wide events only)."""
        for tenant_id in list(self._connections.keys()):
            await self.broadcast_to_tenant(tenant_id, message)

    def get_connection_count(self, tenant_id: Optional[str] = None) -> int:
        if tenant_id:
            return len(self._connections.get(tenant_id, set()))
        return len(self._tenant_map)


# ── Singleton + backward-compat alias ────────────────────────────────────────

manager = ConnectionManager()

# agent_runner.py and tasks.py use websocket_manager.send_to_tenant
websocket_manager = manager

# Convenience alias matching agent_runner usage
ConnectionManager.send_to_tenant = ConnectionManager.broadcast_to_tenant  # type: ignore


async def push_stockout_alert(tenant_id: str, product_name: str, days_remaining: int):
    await manager.broadcast_to_tenant(tenant_id, {
        "type": "stockout_alert",
        "severity": "critical" if days_remaining <= 14 else "warning",
        "product_name": product_name,
        "days_remaining": days_remaining,
        "message": f"⚠️ {product_name} has {days_remaining} days of inventory remaining",
        "action_url": "/inventory",
    })


async def push_opportunity_found(tenant_id: str, product_title: str, opportunity_score: float):
    await manager.broadcast_to_tenant(tenant_id, {
        "type": "opportunity_found",
        "product_title": product_title,
        "opportunity_score": opportunity_score,
        "message": f"🚀 New opportunity: {product_title} (Score: {opportunity_score:.0f}/100)",
        "action_url": "/products",
    })


async def push_agent_update(tenant_id: str, agent_name: str, finding: str):
    await manager.broadcast_to_tenant(tenant_id, {
        "type": "agent_update",
        "agent": agent_name,
        "finding": finding,
    })


async def push_price_alert(tenant_id: str, competitor_name: str, asin: str, old_price: float, new_price: float):
    change_pct = (new_price - old_price) / old_price * 100
    await manager.broadcast_to_tenant(tenant_id, {
        "type": "price_alert",
        "asin": asin,
        "competitor": competitor_name,
        "old_price": old_price,
        "new_price": new_price,
        "change_percent": round(change_pct, 1),
        "message": f"Competitor price change: {asin} went from ${old_price:.2f} → ${new_price:.2f} ({change_pct:+.1f}%)",
        "action_url": "/competitors",
    })


async def push_trend_detected(tenant_id: str, topic: str, score: float, source: str):
    await manager.broadcast_to_tenant(tenant_id, {
        "type": "trend_detected",
        "topic": topic,
        "score": score,
        "source": source,
        "message": f"Trend detected: {topic} (Score: {score:.0f}) via {source}",
        "action_url": "/trends",
    })


async def push_agent_started(tenant_id: str, agent_name: str, run_id: str, task: str = ""):
    await manager.broadcast_to_tenant(tenant_id, {
        "type": "agent_started",
        "agent": agent_name,
        "run_id": run_id,
        "task": task,
        "message": f"Agent {agent_name} started{': ' + task if task else ''}",
    })


async def push_agent_completed(
    tenant_id: str,
    agent_name: str,
    run_id: str,
    findings_count: int = 0,
    summary: str = "",
    status: str = "completed",
):
    await manager.broadcast_to_tenant(tenant_id, {
        "type": "agent_completed",
        "agent": agent_name,
        "run_id": run_id,
        "status": status,
        "findings_count": findings_count,
        "summary": summary or f"{agent_name} found {findings_count} item(s)",
        "message": summary or f"Agent {agent_name} finished with {findings_count} finding(s)",
        "action_url": "/agents",
    })


async def push_inventory_alert(
    tenant_id: str,
    sku: str,
    product_name: str,
    days_remaining: int,
    qty_on_hand: int,
):
    severity = "critical" if days_remaining <= 7 else "warning"
    await manager.broadcast_to_tenant(tenant_id, {
        "type": "inventory_alert",
        "severity": severity,
        "sku": sku,
        "product_name": product_name,
        "days_remaining": days_remaining,
        "qty_on_hand": qty_on_hand,
        "message": f"Low stock: {product_name} — {days_remaining}d remaining ({qty_on_hand} units)",
        "action_url": "/inventory",
    })


async def push_system_status(tenant_id: str, message: str, level: str = "info"):
    """Generic system notification — used for connection confirmation and admin messages."""
    await manager.broadcast_to_tenant(tenant_id, {
        "type": "system",
        "level": level,
        "message": message,
    })
