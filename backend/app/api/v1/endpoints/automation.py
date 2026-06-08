from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID
from app.core.database import get_db
from app.core.security import get_current_user, CurrentUser

router = APIRouter()


@router.get("/workflows")
async def list_workflows(
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    from sqlalchemy import select
    from app.models.remaining_models import Workflow
    q = select(Workflow)
    if is_active is not None:
        q = q.where(Workflow.is_active == is_active)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/workflows")
async def create_workflow(
    workflow: dict,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    user.require("write")
    from app.models.remaining_models import Workflow
    wf = Workflow(**workflow)
    db.add(wf)
    await db.commit()
    await db.refresh(wf)
    return wf


@router.post("/workflows/{workflow_id}/run")
async def run_workflow(
    workflow_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    user.require("write")
    from app.services.automation_service import AutomationService
    service = AutomationService(db, user.tenant_slug)
    return await service.run_workflow(workflow_id)


@router.put("/workflows/{workflow_id}/toggle")
async def toggle_workflow(
    workflow_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    user.require("write")
    from sqlalchemy import select, update
    from app.models.remaining_models import Workflow
    result = await db.execute(select(Workflow).where(Workflow.id == workflow_id))
    wf = result.scalar_one_or_none()
    if not wf:
        raise HTTPException(404, "Workflow not found")
    wf.is_active = not wf.is_active
    await db.commit()
    return {"id": str(workflow_id), "is_active": wf.is_active}


@router.get("/templates")
async def list_templates(user: CurrentUser = Depends(get_current_user)):
    """Pre-built automation templates."""
    return AUTOMATION_TEMPLATES


AUTOMATION_TEMPLATES = [
    {
        "id": "reorder-alert",
        "name": "Low Inventory Reorder Alert",
        "description": "Send email + Slack when inventory drops below reorder point",
        "trigger": "inventory_below_threshold",
        "steps": ["check_inventory", "send_email", "send_slack"],
        "category": "inventory",
    },
    {
        "id": "price-match",
        "name": "Competitor Price Match",
        "description": "Automatically adjust price when competitor goes below yours",
        "trigger": "competitor_price_change",
        "steps": ["check_competitor_price", "calculate_new_price", "update_price"],
        "category": "pricing",
    },
    {
        "id": "high-acos-pause",
        "name": "High ACoS Campaign Pause",
        "description": "Pause campaigns when ACoS exceeds target for 3+ days",
        "trigger": "ppc_acos_threshold",
        "steps": ["check_acos", "pause_campaign", "send_notification"],
        "category": "ppc",
    },
    {
        "id": "new-review-alert",
        "name": "Negative Review Alert",
        "description": "Alert team when 1-2 star review is posted",
        "trigger": "new_review",
        "steps": ["filter_low_reviews", "send_slack", "create_ticket"],
        "category": "reviews",
    },
    {
        "id": "trend-opportunity",
        "name": "Trend Opportunity Alert",
        "description": "Notify when a trend with score >80 is detected in your category",
        "trigger": "trend_detected",
        "steps": ["filter_high_score_trends", "send_email", "create_product_research_task"],
        "category": "trends",
    },
]
