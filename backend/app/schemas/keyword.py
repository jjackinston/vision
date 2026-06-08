from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from uuid import UUID


class KeywordResearchResponse(BaseModel):
    keyword: str
    marketplace: str
    monthly_searches: Optional[int] = None
    search_volume_trend: Optional[float] = None
    cpc: Optional[float] = None
    competition_level: Optional[str] = None
    difficulty_score: Optional[float] = None
    opportunity_score: Optional[float] = None
    ppc_score: Optional[float] = None
    seo_score: Optional[float] = None
    intent: Optional[str] = None
    related_keywords: List[Dict[str, Any]] = []
    long_tail_keywords: List[Dict[str, Any]] = []
    top_ranking_asins: List[str] = []
    ai_insights: Optional[str] = None


class KeywordClusterResponse(BaseModel):
    clusters: List[Dict[str, Any]]
    primary_cluster: Optional[str] = None
    total_keywords: int


class KeywordBulkRequest(BaseModel):
    keywords: List[str] = Field(..., min_items=1, max_items=100)
    marketplace: str = "amazon"


class ReverseASINResponse(BaseModel):
    asin: str
    total_keywords_estimate: Optional[int] = None
    organic_keywords: List[Dict[str, Any]] = []
    sponsored_keywords: List[Dict[str, Any]] = []
    high_value_keywords: List[Dict[str, Any]] = []
    missing_opportunities: List[Dict[str, Any]] = []
