from fastapi import APIRouter, Depends, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID
from app.core.database import get_db
from app.core.security import get_current_user, CurrentUser
from app.services.inventory_service import InventoryService

router = APIRouter()


@router.get("/")
async def list_inventory(
    marketplace: Optional[str] = None,
    warehouse_id: Optional[UUID] = None,
    low_stock_only: bool = False,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    service = InventoryService(db, user.tenant_slug)
    return await service.list_inventory(marketplace, warehouse_id, low_stock_only)


@router.get("/summary")
async def inventory_summary(
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """Aggregated inventory health metrics — total SKUs, units, value, risk counts."""
    service = InventoryService(db, user.tenant_slug)
    return await service.get_inventory_summary(user.tenant_id)


@router.get("/stockout-predictions")
async def stockout_predictions(
    days_threshold: int = Query(30, ge=7, le=90),
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """Predict which products will stock out within the threshold."""
    service = InventoryService(db, user.tenant_slug)
    return await service.predict_stockouts(days_threshold)


@router.get("/reorder-recommendations")
async def reorder_recommendations(
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """Generate AI-powered reorder plan."""
    service = InventoryService(db, user.tenant_slug)
    return await service.generate_reorder_plan()


@router.get("/overstock-analysis")
async def overstock_analysis(
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    service = InventoryService(db, user.tenant_slug)
    return await service.analyze_overstock()


@router.post("/sync")
async def sync_inventory(
    marketplace: Optional[str] = None,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """Module 16: Sync inventory from all connected marketplaces."""
    user.require("write")
    from app.workers.tasks import sync_all_inventory
    background_tasks.add_task(sync_all_inventory.delay)
    return {"message": "Inventory sync queued", "marketplace": marketplace or "all"}


@router.get("/{inventory_id}/history")
async def inventory_history(
    inventory_id: UUID,
    days: int = Query(30, le=365),
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    service = InventoryService(db, user.tenant_slug)
    return await service.get_history(inventory_id, days)


@router.put("/{inventory_id}/reorder-config")
async def update_reorder_config(
    inventory_id: UUID,
    reorder_point: int,
    reorder_quantity: int,
    lead_time_days: int,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    user.require("write")
    service = InventoryService(db, user.tenant_slug)
    return await service.update_reorder_config(inventory_id, reorder_point, reorder_quantity, lead_time_days)


@router.get("/warehouses")
async def list_warehouses(
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    service = InventoryService(db, user.tenant_slug)
    return await service.list_warehouses()
