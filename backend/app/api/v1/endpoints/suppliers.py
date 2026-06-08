from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID
from pydantic import BaseModel
from app.core.database import get_db
from app.core.security import get_current_user, CurrentUser
from app.services.supplier_service import SupplierService

router = APIRouter()


class AnalyzeRequest(BaseModel):
    supplier_name: str
    country: str = "CN"
    website: Optional[str] = None


class NegotiateRequest(BaseModel):
    supplier_id: str = "00000000-0000-0000-0000-000000000000"
    goal: str = "price_reduction"
    current_price: float = 5.0
    target_price: float = 3.80
    current_moq: int = 1000
    target_moq: int = 500


@router.get("/")
async def list_suppliers(
    country: Optional[str] = None,
    min_trust_score: Optional[float] = None,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    service = SupplierService(db, user.tenant_slug)
    return await service.list_suppliers(country, min_trust_score)


@router.post("/analyze")
async def analyze_supplier(
    body: AnalyzeRequest,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """Module 12: AI supplier intelligence — trust, risk, cost, reliability scores."""
    user.require("write")
    service = SupplierService(db, user.tenant_slug)
    return await service.analyze_supplier(body.supplier_name, body.country, body.website)


@router.post("/negotiate")
async def generate_negotiation_script(
    body: NegotiateRequest,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """Module 13: AI Negotiation Assistant — generate scripts for supplier negotiations."""
    user.require("write")
    service = SupplierService(db, user.tenant_slug)
    return await service.generate_negotiation_script(
        body.supplier_id, body.goal, body.current_price, body.target_price,
        body.current_moq, body.target_moq,
    )


@router.post("/{supplier_id}/upload-conversation")
async def upload_conversation(
    supplier_id: UUID,
    conversation: str,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """Upload supplier conversation and get AI negotiation recommendations."""
    user.require("write")
    service = SupplierService(db, user.tenant_slug)
    return await service.analyze_conversation(str(supplier_id), conversation)


@router.get("/{supplier_id}/risk-report")
async def supplier_risk(
    supplier_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    service = SupplierService(db, user.tenant_slug)
    return await service.get_risk_report(str(supplier_id))
