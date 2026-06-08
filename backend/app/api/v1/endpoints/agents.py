from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel
import json
import asyncio

from app.core.database import get_db
from app.core.security import get_current_user, CurrentUser
from app.core.plan_gate import require_plan
from app.agents.agent_system import agent_graph, AgentState
from langchain_core.messages import HumanMessage

router = APIRouter()

AGENT_REGISTRY = {
    "product_research": "Product Research Agent",
    "trend": "Trend Detection Agent",
    "competitor": "Competitor Analysis Agent",
    "inventory": "Inventory Planning Agent",
    "ppc": "PPC Optimization Agent",
    "supplier": "Supplier Intelligence Agent",
    "listing": "Listing Optimization Agent",
}


class AgentRunRequest(BaseModel):
    context: Dict[str, Any] = {}
    task: Optional[str] = None
    priority: str = "normal"


@router.get("/")
async def list_agents(user: CurrentUser = Depends(get_current_user)):
    """List all available agents and their status."""
    return [
        {"id": agent_id, "name": name, "status": "idle", "last_run": None, "findings": 0}
        for agent_id, name in AGENT_REGISTRY.items()
    ]


@router.post("/{agent_name}/run")
async def run_agent(
    agent_name: str,
    request: AgentRunRequest = AgentRunRequest(),
    user: CurrentUser = Depends(require_plan("professional")),
):
    """Trigger a single agent run."""
    user.require("write")
    if agent_name not in AGENT_REGISTRY:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")

    import uuid, threading
    run_id = str(uuid.uuid4())
    task_label = request.task or AGENT_REGISTRY.get(agent_name, agent_name)
    _priority = 8 if request.priority == "high" else 5

    # Emit agent_started WebSocket event immediately (non-blocking)
    async def _emit_started():
        try:
            from app.websocket.manager import push_agent_started
            await push_agent_started(
                tenant_id=str(user.tenant_id),
                agent_name=AGENT_REGISTRY.get(agent_name, agent_name),
                run_id=run_id,
                task=task_label,
            )
        except Exception:
            pass

    asyncio.create_task(_emit_started())

    # Fire-and-forget via daemon thread so the endpoint returns immediately
    # even when Redis/Celery is unavailable (avoids blocking on connection timeout)
    def _queue():
        try:
            from app.workers.tasks import celery_app
            celery_app.send_task(
                "app.workers.tasks.run_single_agent",
                args=[agent_name, task_label, user.tenant_id, run_id],
                priority=_priority,
            )
        except Exception:
            pass

    threading.Thread(target=_queue, daemon=True).start()

    return {"run_id": run_id, "agent": agent_name, "status": "queued", "task": task_label}


@router.get("/statuses")
async def get_all_statuses(user: CurrentUser = Depends(get_current_user)):
    """Get real-time status of all agents for this tenant."""
    from app.agents.agent_system import get_orchestrator
    orchestrator = get_orchestrator(user.tenant_id)
    statuses = orchestrator.get_all_statuses()
    return {s["type"]: s for s in statuses}


@router.post("/run-all")
async def run_all_agents(
    body: dict = None,
    user: CurrentUser = Depends(get_current_user),
):
    """Trigger all 7 agents in parallel."""
    user.require("write")
    from app.agents.agent_system import get_orchestrator
    orchestrator = get_orchestrator(user.tenant_id)
    context = (body or {}).get("context", {})
    result = await orchestrator.run_all_agents(context)
    return result


@router.get("/intelligence")
async def get_aggregated_intelligence(user: CurrentUser = Depends(get_current_user)):
    """Get aggregated intelligence from all agents."""
    from app.agents.agent_system import get_orchestrator
    orchestrator = get_orchestrator(user.tenant_id)
    return await orchestrator.get_aggregated_intelligence()


@router.get("/runs/{run_id}")
async def get_run(
    run_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    from sqlalchemy import select
    from app.models.remaining_models import AgentRun
    result = await db.execute(select(AgentRun).where(AgentRun.id == run_id))
    run = result.scalar_one_or_none()
    if not run:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Agent run not found")
    return run


@router.post("/chat/stream")
async def agent_chat_stream(
    message: str,
    user: CurrentUser = Depends(get_current_user),
):
    """Stream multi-agent response via Server-Sent Events."""
    async def generate():
        state = AgentState(
            messages=[HumanMessage(content=message)],
            tenant_id=user.tenant_id,
            task_type="chat",
            context={},
            results={},
            next_agent="product_research",
        )
        async for chunk in agent_graph.astream(state):
            for node, output in chunk.items():
                messages = output.get("messages", [])
                for msg in messages:
                    if hasattr(msg, "content"):
                        yield f"data: {json.dumps({'node': node, 'content': msg.content})}\n\n"
                        await asyncio.sleep(0)
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.get("/runs")
async def list_runs(
    agent_name: Optional[str] = None,
    limit: int = Query(20, le=100),
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    from sqlalchemy import select, desc
    from app.models.remaining_models import AgentRun
    q = select(AgentRun).order_by(desc(AgentRun.started_at)).limit(limit)
    if agent_name:
        q = q.where(AgentRun.agent_type == agent_name)
    result = await db.execute(q)
    return result.scalars().all()
