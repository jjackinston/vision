from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from decimal import Decimal


class ProductCreate(BaseModel):
    title: str
    asin: Optional[str] = None
    marketplace: str = "amazon"
    category: Optional[str] = None
    current_price: Optional[Decimal] = None


class ProductSearchRequest(BaseModel):
    query: str
    marketplace: str = "amazon"
    category: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_monthly_revenue: Optional[float] = None
    max_results: int = Field(default=20, le=100)


class ProductResponse(BaseModel):
    id: UUID
    title: str
    asin: Optional[str]
    marketplace: str
    category: Optional[str]
    current_price: Optional[Decimal]
    opportunity_score: Optional[float]
    risk_score: Optional[float]
    profit_score: Optional[float]
    competition_score: Optional[float]
    market_entry_score: Optional[float]
    is_tracked: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    items: List[ProductResponse]
    total: int
    page: int
    per_page: int


class ProductOpportunityScore(BaseModel):
    opportunity_score: float = Field(ge=0, le=100)
    risk_score: float = Field(ge=0, le=100)
    profit_score: float = Field(ge=0, le=100)
    competition_score: float = Field(ge=0, le=100)
    market_entry_score: float = Field(ge=0, le=100)
    prediction_30d_units: int
    prediction_90d_units: int
    prediction_180d_units: int
    prediction_12m_revenue: float
    reasoning: str
    action_recommendation: str


class ProductSuccessPrediction(BaseModel):
    success_probability: float = Field(ge=0, le=100)
    estimated_revenue_monthly: float
    estimated_profit_monthly: float
    break_even_months: int
    risk_factors: List[str]
    opportunities: List[str]
    recommendation: str  # launch, wait, avoid
    explainable_reasoning: str


class SaturationRadar(BaseModel):
    current_saturation_score: float
    saturation_3m: float
    saturation_6m: float
    saturation_12m: float
    new_seller_velocity: str
    review_velocity_trend: str
    entry_risk_score: float
    exit_risk_score: float
    heat_map_data: List[Dict[str, Any]]
    recommendation: str


class LaunchSimulatorInput(BaseModel):
    product_cost: float
    inventory_quantity: int
    ppc_budget_daily: float
    selling_price: float
    marketplace: str = "amazon"
    target_bsr: Optional[int] = None
    launch_strategy: str = "aggressive"


class LaunchScenario(BaseModel):
    scenario: str  # conservative, realistic, optimistic
    weekly_revenue: List[float]  # 4 weeks
    monthly_cash_flow: List[float]  # 6 months
    break_even_date: str
    profit_6m: float
    profit_12m: float
    roi_percent: float
    inventory_depleted_date: str


class LaunchSimulatorResult(BaseModel):
    scenarios: Dict[str, LaunchScenario]
    recommended_scenario: str
    key_assumptions: List[str]
    warnings: List[str]
