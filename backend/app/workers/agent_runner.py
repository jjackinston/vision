"""
Agent Runner — standalone process that runs the 7 AI agents on schedule.
Called via K8s Deployment: python -m app.workers.agent_runner
"""
import asyncio
import logging
import signal
from datetime import datetime, timedelta
from typing import Any

from app.core.config import settings
from app.core.cache import get_redis

logger = logging.getLogger(__name__)

AGENT_SCHEDULES = {
    "product_research": timedelta(hours=6),
    "trend": timedelta(hours=2),
    "competitor": timedelta(hours=4),
    "inventory": timedelta(hours=1),
    "ppc": timedelta(hours=6),
    "supplier": timedelta(hours=12),
    "listing": timedelta(hours=24),
}

_running = True


def handle_shutdown(signum, frame):
    global _running
    logger.info("Shutdown signal received")
    _running = False


async def get_active_tenants() -> list[dict]:
    """Fetch all active tenants from database."""
    try:
        from app.core.database import AsyncSessionLocal
        from app.models.tenant import Tenant
        from sqlalchemy import select
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Tenant).where(Tenant.is_active == True)
            )
            tenants = result.scalars().all()
            return [{"id": str(t.id), "slug": t.slug} for t in tenants]
    except Exception as e:
        logger.error(f"Failed to fetch tenants: {e}")
        return []


async def should_run_agent(tenant_id: str, agent_type: str) -> bool:
    """Check if agent is due to run based on schedule."""
    redis = await get_redis()
    key = f"agent_last_run:{tenant_id}:{agent_type}"
    last_run = await redis.get(key)

    if not last_run:
        return True

    schedule = AGENT_SCHEDULES.get(agent_type, timedelta(hours=6))
    last_run_dt = datetime.fromisoformat(last_run.decode())
    return datetime.now() - last_run_dt >= schedule


async def mark_agent_ran(tenant_id: str, agent_type: str):
    """Mark agent as just-ran in Redis."""
    redis = await get_redis()
    key = f"agent_last_run:{tenant_id}:{agent_type}"
    await redis.set(key, datetime.now().isoformat(), ex=int(timedelta(days=7).total_seconds()))


async def run_agents_for_tenant(tenant_id: str, tenant_slug: str):
    """Run all due agents for a single tenant."""
    from app.agents.agent_system import get_orchestrator, AgentType

    orchestrator = get_orchestrator(tenant_id)

    for agent_type in AgentType:
        if not _running:
            break

        if not await should_run_agent(tenant_id, agent_type.value):
            continue

        try:
            logger.info(f"Running {agent_type.value} agent for tenant {tenant_slug}")
            result = await orchestrator.run_agent(agent_type)

            if result.get("status") == "success":
                await mark_agent_ran(tenant_id, agent_type.value)
                findings = result.get("findings_count", 0)
                logger.info(f"Agent {agent_type.value} completed: {findings} findings for {tenant_slug}")

                if findings > 0:
                    await _notify_findings(tenant_id, agent_type.value, result)
            else:
                logger.error(f"Agent {agent_type.value} failed for {tenant_slug}: {result.get('error')}")

        except Exception as e:
            logger.error(f"Agent {agent_type.value} exception for {tenant_slug}: {e}")


async def _notify_findings(tenant_id: str, agent_type: str, result: dict):
    """Send WebSocket notification for agent findings."""
    try:
        from app.websocket.manager import websocket_manager
        await websocket_manager.send_to_tenant(tenant_id, {
            "type": "agent_findings",
            "agent": agent_type,
            "findings_count": result.get("findings_count", 0),
            "findings": result.get("findings", [])[:3],
            "timestamp": datetime.now().isoformat(),
        })
    except Exception:
        pass


async def main():
    """Main agent runner loop."""
    signal.signal(signal.SIGTERM, handle_shutdown)
    signal.signal(signal.SIGINT, handle_shutdown)

    logger.info("SellerVision AI Agent Runner starting...")

    while _running:
        try:
            tenants = await get_active_tenants()
            if not tenants:
                logger.info("No active tenants found, waiting...")
                await asyncio.sleep(60)
                continue

            logger.info(f"Running agents for {len(tenants)} tenants")

            tasks = [
                run_agents_for_tenant(t["id"], t["slug"])
                for t in tenants
            ]
            await asyncio.gather(*tasks, return_exceptions=True)

        except Exception as e:
            logger.error(f"Agent runner loop error: {e}")

        await asyncio.sleep(60)

    logger.info("Agent runner stopped")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
