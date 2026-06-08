"""
SellerVision AI — Multi-Agent System (Module 21)
LangChain-based autonomous agents that collaborate continuously.
Each agent has specialized tools and communicates via shared state.
"""
from typing import Any, TypedDict, Annotated
from enum import Enum
import operator
import json
import asyncio
from datetime import datetime, timezone

try:
    from langchain_openai import ChatOpenAI
    from langchain_anthropic import ChatAnthropic
    from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
    from langchain_core.tools import tool
    from langgraph.graph import StateGraph, END
    from langgraph.prebuilt import ToolNode
    _LANGCHAIN_AVAILABLE = True
except ImportError:
    _LANGCHAIN_AVAILABLE = False
    tool = lambda f: f  # noqa: E731 — passthrough when not installed

from app.core.config import settings


# ============================================================
# SHARED AGENT STATE
# ============================================================
class AgentState(TypedDict):
    messages: Annotated[list, operator.add]
    tenant_id: str
    task_type: str
    context: dict
    results: dict
    next_agent: str


# ============================================================
# TOOLS
# ============================================================
@tool
async def search_amazon_products(query: str, category: str = "", max_results: int = 20) -> dict:
    """Search Amazon marketplace for products matching the query."""
    from app.integrations.amazon.sp_api import AmazonSPAPI
    api = AmazonSPAPI()
    return await api.search_catalog(query, category, max_results)


@tool
async def get_keyword_data(keyword: str, marketplace: str = "amazon") -> dict:
    """Get search volume, CPC, competition data for a keyword."""
    from app.services.keyword_service import KeywordService
    service = KeywordService()
    return await service.get_keyword_metrics(keyword, marketplace)


@tool
async def get_competitor_reviews(asin: str, max_reviews: int = 100) -> list:
    """Get and analyze competitor reviews for weakness patterns."""
    from app.integrations.amazon.sp_api import AmazonSPAPI
    api = AmazonSPAPI()
    return await api.get_reviews(asin, max_reviews)


@tool
async def get_inventory_status(tenant_id: str) -> dict:
    """Get current inventory levels and stockout predictions."""
    from app.services.inventory_service import InventoryService
    service = InventoryService()
    return await service.get_inventory_summary(tenant_id)


@tool
async def get_ppc_performance(tenant_id: str, days: int = 30) -> dict:
    """Get PPC campaign performance data."""
    from app.services.ppc_service import PPCService
    service = PPCService()
    return await service.get_performance_summary(tenant_id, days)


@tool
async def get_trend_data(topic: str, sources: list = None) -> dict:
    """Get trend data from Google Trends, TikTok, Reddit."""
    from app.services.trend_service import TrendService
    service = TrendService()
    return await service.get_trend_data(topic, sources or ["google", "tiktok", "reddit"])


@tool
async def analyze_supplier(supplier_name: str, country: str = "CN") -> dict:
    """Analyze supplier reliability, cost, and risk."""
    from app.services.supplier_service import SupplierService
    service = SupplierService()
    return await service.analyze_supplier(supplier_name, country)


@tool
async def optimize_listing(product_id: str, marketplace: str) -> dict:
    """Generate optimized listing content for a product."""
    from app.services.listing_service import ListingService
    service = ListingService()
    # generate_ai_listing expects product_data dict + marketplace; fetch basic data first
    product_data = {"id": product_id, "title": f"Product {product_id}", "marketplace": marketplace}
    return await service.generate_ai_listing(product_data, marketplace)


# ============================================================
# AGENT DEFINITIONS
# ============================================================

PRODUCT_RESEARCH_AGENT_PROMPT = """You are the Product Research Agent for SellerVision AI.
Your mission: Continuously identify high-opportunity products across all marketplaces.
Analyze: demand signals, competition gaps, profit potential, trend momentum.
Always score opportunities on a 0-100 scale and prioritize by profit potential.
Report findings in structured JSON. When you identify a strong opportunity (>70 score),
notify the Listing Agent and Inventory Agent."""

TREND_AGENT_PROMPT = """You are the Trend Detection Agent for SellerVision AI.
Your mission: Monitor Google Trends, TikTok, Reddit, Pinterest, YouTube for emerging trends.
Identify: viral products, seasonal opportunities, emerging categories.
Predict: trend lifespan, peak date, commercial viability.
Alert the Product Research Agent when a monetizable trend is detected."""

COMPETITOR_AGENT_PROMPT = """You are the Competitor Analysis Agent for SellerVision AI.
Your mission: Monitor competitors' pricing, inventory, reviews, and listings.
Detect: price changes, stockouts, review patterns, listing changes.
Generate: competitive intelligence reports, weakness analysis, counter-strategies.
Update the AI CEO Dashboard with competitive threats and opportunities."""

INVENTORY_AGENT_PROMPT = """You are the Inventory Planning Agent for SellerVision AI.
Your mission: Predict stockouts and overstock events before they happen.
Monitor: inventory levels, sales velocity, supplier lead times, seasonal patterns.
Generate: reorder recommendations, purchase orders, cash flow projections.
Alert when stockout is predicted within 14 days."""

PPC_AGENT_PROMPT = """You are the PPC Optimization Agent for SellerVision AI.
Your mission: Continuously optimize advertising campaigns for maximum ROAS.
Monitor: ACoS, TACoS, bid efficiency, keyword performance, wasted spend.
Actions: bid adjustments, keyword harvesting, negative keyword additions, budget reallocation.
Target: ACoS below category benchmark, TACoS < 10%."""

SUPPLIER_AGENT_PROMPT = """You are the Supplier Intelligence Agent for SellerVision AI.
Your mission: Monitor supplier performance, costs, and risks.
Track: lead times, quality scores, MOQ changes, geopolitical risks.
Generate: negotiation opportunities, alternative supplier recommendations.
Alert when a supplier risk score exceeds 70."""

LISTING_AGENT_PROMPT = """You are the Listing Optimization Agent for SellerVision AI.
Your mission: Maintain peak-performing listings across all marketplaces.
Monitor: keyword rankings, conversion rates, CTR, A/B test results.
Generate: optimized titles, bullets, descriptions, keyword suggestions.
Ensure all listings are indexed for target keywords."""


# ============================================================
# AGENT FACTORY
# ============================================================
class AgentFactory:
    def __init__(self):
        if not _LANGCHAIN_AVAILABLE:
            raise RuntimeError("langchain packages not installed")
        openai_key = settings.OPENAI_API_KEY or "placeholder"
        anthropic_key = settings.ANTHROPIC_API_KEY or "placeholder"
        self.gpt4o = ChatOpenAI(model=settings.OPENAI_MODEL, temperature=0, api_key=openai_key)
        self.claude = ChatAnthropic(model=settings.ANTHROPIC_MODEL, api_key=anthropic_key)

        self.tools = [
            search_amazon_products,
            get_keyword_data,
            get_competitor_reviews,
            get_inventory_status,
            get_ppc_performance,
            get_trend_data,
            analyze_supplier,
            optimize_listing,
        ]

    def create_product_research_agent(self):
        return self.gpt4o.bind_tools(self.tools)

    def create_trend_agent(self):
        return self.gpt4o.bind_tools([get_trend_data, search_amazon_products, get_keyword_data])

    def create_competitor_agent(self):
        return self.claude.bind_tools([get_competitor_reviews, search_amazon_products])

    def create_inventory_agent(self):
        return self.gpt4o.bind_tools([get_inventory_status])

    def create_ppc_agent(self):
        return self.gpt4o.bind_tools([get_ppc_performance, get_keyword_data])

    def create_supplier_agent(self):
        return self.claude.bind_tools([analyze_supplier])

    def create_listing_agent(self):
        return self.claude.bind_tools([optimize_listing, get_keyword_data])


# ============================================================
# MULTI-AGENT ORCHESTRATOR GRAPH (LangGraph)
# ============================================================
def build_agent_graph():
    if not _LANGCHAIN_AVAILABLE:
        raise RuntimeError("langchain/langgraph not installed — cannot build agent graph")
    factory = AgentFactory()
    tool_node = ToolNode(factory.tools)

    async def product_research_node(state: AgentState) -> AgentState:
        agent = factory.create_product_research_agent()
        messages = [SystemMessage(content=PRODUCT_RESEARCH_AGENT_PROMPT)] + state["messages"]
        response = await agent.ainvoke(messages)
        return {"messages": [response], "next_agent": "trend" if state["task_type"] == "full_scan" else END}

    async def trend_node(state: AgentState) -> AgentState:
        agent = factory.create_trend_agent()
        messages = [SystemMessage(content=TREND_AGENT_PROMPT)] + state["messages"]
        response = await agent.ainvoke(messages)
        return {"messages": [response], "next_agent": "competitor"}

    async def competitor_node(state: AgentState) -> AgentState:
        agent = factory.create_competitor_agent()
        messages = [SystemMessage(content=COMPETITOR_AGENT_PROMPT)] + state["messages"]
        response = await agent.ainvoke(messages)
        return {"messages": [response], "next_agent": "inventory"}

    async def inventory_node(state: AgentState) -> AgentState:
        agent = factory.create_inventory_agent()
        messages = [SystemMessage(content=INVENTORY_AGENT_PROMPT)] + state["messages"]
        response = await agent.ainvoke(messages)
        return {"messages": [response], "next_agent": "ppc"}

    async def ppc_node(state: AgentState) -> AgentState:
        agent = factory.create_ppc_agent()
        messages = [SystemMessage(content=PPC_AGENT_PROMPT)] + state["messages"]
        response = await agent.ainvoke(messages)
        return {"messages": [response], "next_agent": END}

    def router(state: AgentState) -> str:
        return state.get("next_agent", END)

    graph = StateGraph(AgentState)
    graph.add_node("product_research", product_research_node)
    graph.add_node("trend", trend_node)
    graph.add_node("competitor", competitor_node)
    graph.add_node("inventory", inventory_node)
    graph.add_node("ppc", ppc_node)
    graph.add_node("tools", tool_node)

    graph.set_entry_point("product_research")
    graph.add_conditional_edges("product_research", router, {"trend": "trend", END: END})
    graph.add_conditional_edges("trend", router, {"competitor": "competitor", END: END})
    graph.add_conditional_edges("competitor", router, {"inventory": "inventory", END: END})
    graph.add_conditional_edges("inventory", router, {"ppc": "ppc", END: END})
    graph.add_edge("ppc", END)

    return graph.compile()


# ============================================================
# LAZY GRAPH INITIALIZATION — avoids startup crash without API keys
# ============================================================
_agent_graph = None


def get_agent_graph():
    global _agent_graph
    if _agent_graph is None:
        _agent_graph = build_agent_graph()
    return _agent_graph


# Backward-compat alias — do not call at module load
agent_graph = None


# ============================================================
# AGENT TYPE ENUM
# ============================================================
class AgentType(str, Enum):
    PRODUCT_RESEARCH = "product_research"
    TREND = "trend"
    COMPETITOR = "competitor"
    INVENTORY = "inventory"
    PPC = "ppc"
    SUPPLIER = "supplier"
    LISTING = "listing"


# ============================================================
# AGENT ORCHESTRATOR
# ============================================================
class AgentOrchestrator:
    """Manages all 7 agents for a single tenant."""

    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self._statuses: dict[str, dict] = {
            at.value: {"type": at.value, "status": "idle", "last_run": None, "findings": 0}
            for at in AgentType
        }

    def get_all_statuses(self) -> list[dict]:
        return list(self._statuses.values())

    async def run_agent(self, agent_type: AgentType, context: dict = None) -> dict:
        """Run a single agent and return its findings."""
        started_at = datetime.now(timezone.utc).isoformat()
        self._statuses[agent_type.value]["status"] = "running"
        try:
            graph = get_agent_graph()
            state = AgentState(
                messages=[],
                tenant_id=self.tenant_id,
                task_type=agent_type.value,
                context=context or {},
                results={},
                next_agent=agent_type.value,
            )
            final_state = await graph.ainvoke(state)
            findings_count = len(final_state.get("messages", []))
            self._statuses[agent_type.value].update({
                "status": "idle",
                "last_run": started_at,
                "findings": findings_count,
            })
            return {
                "status": "completed",
                "agent_type": agent_type.value,
                "tenant_id": self.tenant_id,
                "findings_count": findings_count,
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "messages": [m.content for m in final_state.get("messages", []) if hasattr(m, "content")],
            }
        except Exception as e:
            self._statuses[agent_type.value]["status"] = "error"
            return {"status": "error", "agent_type": agent_type.value, "error": str(e)}

    async def run_all_agents(self, context: dict = None) -> dict:
        """Run all 7 agents concurrently."""
        tasks = [self.run_agent(at, context) for at in AgentType]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        findings_total = sum(
            r.get("findings_count", 0) for r in results if isinstance(r, dict)
        )
        return {
            "status": "completed",
            "tenant_id": self.tenant_id,
            "total_findings": findings_total,
            "agents": [r if isinstance(r, dict) else {"status": "error", "error": str(r)} for r in results],
        }

    async def get_aggregated_intelligence(self) -> dict:
        """Return cached status + last findings across all agents."""
        return {
            "tenant_id": self.tenant_id,
            "statuses": self._statuses,
            "summary": {
                "total_agents": len(AgentType),
                "running": sum(1 for s in self._statuses.values() if s["status"] == "running"),
                "total_findings": sum(s["findings"] for s in self._statuses.values()),
            },
        }


_orchestrators: dict[str, AgentOrchestrator] = {}


def get_orchestrator(tenant_id: str) -> AgentOrchestrator:
    if tenant_id not in _orchestrators:
        _orchestrators[tenant_id] = AgentOrchestrator(tenant_id)
    return _orchestrators[tenant_id]
