"""Seed initial plans into the database."""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import AsyncSessionLocal
from app.models.tenant import Plan


PLANS = [
    {
        "name": "starter",
        "price_monthly": 49.00,
        "price_annual": 470.00,
        "limits": {
            "products": 50, "keywords": 200, "api_calls_monthly": 5000,
            "users": 1, "marketplaces": 2, "ai_agents": 2,
        },
        "features": {
            "modules": ["product_research", "keyword_intelligence", "ceo_dashboard",
                        "profit_calculator", "listing_builder"],
            "support": "email",
            "white_label": False,
        },
    },
    {
        "name": "professional",
        "price_monthly": 149.00,
        "price_annual": 1430.00,
        "limits": {
            "products": 250, "keywords": 1000, "api_calls_monthly": 25000,
            "users": 3, "marketplaces": 4, "ai_agents": 5,
        },
        "features": {
            "modules": ["all_starter", "launch_simulator", "saturation_radar",
                        "competitor_weakness_scanner", "ai_product_creator",
                        "trend_discovery", "inventory_command_center"],
            "support": "priority_email",
            "white_label": False,
        },
    },
    {
        "name": "business",
        "price_monthly": 299.00,
        "price_annual": 2870.00,
        "limits": {
            "products": 1000, "keywords": 5000, "api_calls_monthly": 100000,
            "users": 10, "marketplaces": 6, "ai_agents": 7,
        },
        "features": {
            "modules": ["all_modules"],
            "support": "live_chat",
            "white_label": False,
            "digital_twin": True,
            "voice_assistant": True,
            "automation": True,
            "marketplace": True,
        },
    },
    {
        "name": "agency",
        "price_monthly": 499.00,
        "price_annual": 4790.00,
        "limits": {
            "products": -1, "keywords": -1, "api_calls_monthly": 500000,
            "users": 25, "marketplaces": 6, "ai_agents": 7,
        },
        "features": {
            "modules": ["all_modules"],
            "support": "dedicated_slack",
            "white_label": True,
            "multi_account": True,
            "agency_dashboard": True,
        },
    },
    {
        "name": "enterprise",
        "price_monthly": 0.00,
        "price_annual": 0.00,
        "limits": {
            "products": -1, "keywords": -1, "api_calls_monthly": -1,
            "users": -1, "marketplaces": 6, "ai_agents": -1,
        },
        "features": {
            "modules": ["all_modules"],
            "support": "dedicated_csm",
            "white_label": True,
            "custom_ai_models": True,
            "sso": True,
            "soc2": True,
            "dedicated_infrastructure": True,
            "sla_99_9": True,
        },
    },
]


async def seed():
    async with AsyncSessionLocal() as db:
        from sqlalchemy import select
        existing = await db.execute(select(Plan))
        if existing.scalars().first():
            print("Plans already seeded.")
            return
        for plan_data in PLANS:
            plan = Plan(**plan_data)
            db.add(plan)
        await db.commit()
        print(f"Seeded {len(PLANS)} plans.")


if __name__ == "__main__":
    asyncio.run(seed())
