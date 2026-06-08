#!/usr/bin/env python3
"""
SellerVision AI — Database Seed Script
=======================================
Idempotent: safe to run multiple times — skips rows that already exist.

Seeds:
  1. Plans        — Starter / Professional / Business / Agency
  2. Dev tenant   — for the dev auth bypass (tenant_slug = "dev-seller")
  3. Dev user     — paired with dev tenant
  4. Products     — 8 realistic Amazon products with scores
  5. Keywords     — 10 high-opportunity keywords
  6. Inventory    — warehouse + stock levels for the dev tenant products

Usage:
    # From repo root, with the DB running:
    python backend/scripts/seed.py

    # Against a specific DB:
    DATABASE_URL=postgresql+asyncpg://... python backend/scripts/seed.py

    # Plans only (safe for production — no demo data):
    python backend/scripts/seed.py --plans-only
"""
import asyncio
import sys
import os
import argparse
from decimal import Decimal
from datetime import datetime, timezone, timedelta

# Allow running from repo root or from backend/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, text


# ── Config ────────────────────────────────────────────────────────────
DEV_TENANT_ID   = "11111111-1111-1111-1111-111111111111"
DEV_TENANT_SLUG = "dev-seller"
DEV_USER_ID     = "22222222-2222-2222-2222-222222222222"
DEV_USER_EMAIL  = "dev@sellervision.local"

PLAN_DATA = [
    {
        "name": "Starter",
        "price_monthly": Decimal("49.00"),
        "price_annual":  Decimal("470.00"),  # ~20% off
        "limits": {
            "products": 50, "keywords": 500, "api_calls": 10000,
            "users": 1, "marketplaces": 2, "agents": 2,
        },
        "features": {
            "ai_analysis": True, "competitor_tracking": False, "ppc_automation": False,
            "custom_reports": False, "api_access": False, "white_label": False,
        },
    },
    {
        "name": "Professional",
        "price_monthly": Decimal("149.00"),
        "price_annual":  Decimal("1430.00"),
        "limits": {
            "products": 100, "keywords": 5000, "api_calls": 100000,
            "users": 3, "marketplaces": 4, "agents": 5,
        },
        "features": {
            "ai_analysis": True, "competitor_tracking": True, "ppc_automation": True,
            "custom_reports": False, "api_access": False, "white_label": False,
        },
    },
    {
        "name": "Business",
        "price_monthly": Decimal("299.00"),
        "price_annual":  Decimal("2870.00"),
        "limits": {
            "products": 500, "keywords": 25000, "api_calls": 500000,
            "users": 10, "marketplaces": 6, "agents": 7,
        },
        "features": {
            "ai_analysis": True, "competitor_tracking": True, "ppc_automation": True,
            "custom_reports": True, "api_access": True, "white_label": False,
        },
    },
    {
        "name": "Agency",
        "price_monthly": Decimal("599.00"),
        "price_annual":  Decimal("5750.00"),
        "limits": {
            "products": -1, "keywords": -1, "api_calls": -1,
            "users": 25, "marketplaces": 6, "agents": 7,
        },
        "features": {
            "ai_analysis": True, "competitor_tracking": True, "ppc_automation": True,
            "custom_reports": True, "api_access": True, "white_label": True,
        },
    },
]

PRODUCTS = [
    {
        "asin": "B09XQ3MRNT", "title": "Ergonomic Lumbar Support Cushion for Office Chair",
        "brand": "ComfortPro", "category": "Home & Office", "subcategory": "Chair Accessories",
        "marketplace": "amazon", "current_price": Decimal("34.99"), "buy_box_price": Decimal("34.99"),
        "cost": Decimal("8.50"), "opportunity_score": Decimal("87.4"), "risk_score": Decimal("22.0"),
        "profit_score": Decimal("76.5"), "competition_score": Decimal("45.0"),
        "market_entry_score": Decimal("68.0"), "is_tracked": True, "is_own_product": True,
        "tags": ["ergonomic", "office", "back-support"],
        "image_urls": ["https://m.media-amazon.com/images/placeholder1.jpg"],
    },
    {
        "asin": "B0BQTL89PR", "title": "Stainless Steel Insulated Water Bottle 32oz",
        "brand": "HydroMax", "category": "Sports & Outdoors", "subcategory": "Water Bottles",
        "marketplace": "amazon", "current_price": Decimal("24.99"), "buy_box_price": Decimal("24.99"),
        "cost": Decimal("6.20"), "opportunity_score": Decimal("82.1"), "risk_score": Decimal("31.0"),
        "profit_score": Decimal("71.0"), "competition_score": Decimal("62.0"),
        "market_entry_score": Decimal("55.0"), "is_tracked": True, "is_own_product": True,
        "tags": ["hydration", "BPA-free", "insulated"],
        "image_urls": ["https://m.media-amazon.com/images/placeholder2.jpg"],
    },
    {
        "asin": "B07FJSQ8VZ", "title": "LED Desk Lamp with USB Charging Port & Touch Control",
        "brand": "BrightWork", "category": "Home & Office", "subcategory": "Desk Lamps",
        "marketplace": "amazon", "current_price": Decimal("42.99"), "buy_box_price": Decimal("41.50"),
        "cost": Decimal("11.00"), "opportunity_score": Decimal("79.8"), "risk_score": Decimal("28.0"),
        "profit_score": Decimal("68.2"), "competition_score": Decimal("58.0"),
        "market_entry_score": Decimal("61.0"), "is_tracked": True, "is_own_product": False,
        "tags": ["lighting", "USB", "touch-control"],
        "image_urls": ["https://m.media-amazon.com/images/placeholder3.jpg"],
    },
    {
        "asin": "B08N5Y8P2Q", "title": "Non-Slip Silicone Kitchen Mat, Set of 2",
        "brand": "KitchenEase", "category": "Kitchen & Dining", "subcategory": "Kitchen Mats",
        "marketplace": "amazon", "current_price": Decimal("18.99"), "buy_box_price": Decimal("18.99"),
        "cost": Decimal("4.30"), "opportunity_score": Decimal("74.3"), "risk_score": Decimal("19.0"),
        "profit_score": Decimal("65.0"), "competition_score": Decimal("41.0"),
        "market_entry_score": Decimal("73.0"), "is_tracked": True, "is_own_product": True,
        "tags": ["kitchen", "non-slip", "silicone"],
        "image_urls": ["https://m.media-amazon.com/images/placeholder4.jpg"],
    },
    {
        "asin": "B09V3QRPM1", "title": "Cable Management Box with 6-Outlet Power Strip",
        "brand": "NeatDesk", "category": "Electronics", "subcategory": "Power Strips",
        "marketplace": "amazon", "current_price": Decimal("29.99"), "buy_box_price": Decimal("28.50"),
        "cost": Decimal("7.80"), "opportunity_score": Decimal("71.6"), "risk_score": Decimal("35.0"),
        "profit_score": Decimal("62.4"), "competition_score": Decimal("55.0"),
        "market_entry_score": Decimal("49.0"), "is_tracked": True, "is_own_product": False,
        "tags": ["cable-management", "power-strip", "home-office"],
        "image_urls": ["https://m.media-amazon.com/images/placeholder5.jpg"],
    },
    {
        "asin": "B0BTMK1L2X", "title": "Bamboo Cutting Board Set with Juice Groove, 3-Piece",
        "brand": "GreenChef", "category": "Kitchen & Dining", "subcategory": "Cutting Boards",
        "marketplace": "amazon", "current_price": Decimal("27.99"), "buy_box_price": Decimal("27.99"),
        "cost": Decimal("7.10"), "opportunity_score": Decimal("69.2"), "risk_score": Decimal("24.0"),
        "profit_score": Decimal("60.8"), "competition_score": Decimal("48.0"),
        "market_entry_score": Decimal("64.0"), "is_tracked": True, "is_own_product": True,
        "tags": ["bamboo", "cutting-board", "eco-friendly"],
        "image_urls": ["https://m.media-amazon.com/images/placeholder6.jpg"],
    },
    {
        "asin": "B0C2HNXP4W", "title": "Resistance Bands Set for Home Workout — 5 Levels",
        "brand": "FitPulse", "category": "Sports & Outdoors", "subcategory": "Resistance Bands",
        "marketplace": "amazon", "current_price": Decimal("19.99"), "buy_box_price": Decimal("19.99"),
        "cost": Decimal("4.60"), "opportunity_score": Decimal("85.7"), "risk_score": Decimal("27.0"),
        "profit_score": Decimal("73.1"), "competition_score": Decimal("67.0"),
        "market_entry_score": Decimal("52.0"), "is_tracked": True, "is_own_product": True,
        "tags": ["fitness", "home-gym", "resistance-training"],
        "image_urls": ["https://m.media-amazon.com/images/placeholder7.jpg"],
    },
    {
        "asin": "B08K3RKHPF", "title": "Portable Phone Stand Adjustable Desk Holder, 2-Pack",
        "brand": "DeskPal", "category": "Electronics", "subcategory": "Phone Accessories",
        "marketplace": "amazon", "current_price": Decimal("13.99"), "buy_box_price": Decimal("13.99"),
        "cost": Decimal("2.90"), "opportunity_score": Decimal("66.9"), "risk_score": Decimal("41.0"),
        "profit_score": Decimal("58.3"), "competition_score": Decimal("74.0"),
        "market_entry_score": Decimal("43.0"), "is_tracked": False, "is_own_product": False,
        "tags": ["phone-stand", "desk-accessory", "portable"],
        "image_urls": ["https://m.media-amazon.com/images/placeholder8.jpg"],
    },
]

KEYWORDS = [
    {"keyword": "ergonomic office chair cushion",   "marketplace": "amazon", "monthly_searches": 74200, "cpc": Decimal("1.42"), "competition_level": "medium", "difficulty_score": Decimal("48.0"), "opportunity_score": Decimal("82.0"), "intent": "purchase"},
    {"keyword": "insulated water bottle 32oz",       "marketplace": "amazon", "monthly_searches": 135000, "cpc": Decimal("0.98"), "competition_level": "high",   "difficulty_score": Decimal("67.0"), "opportunity_score": Decimal("71.0"), "intent": "purchase"},
    {"keyword": "LED desk lamp USB charging",        "marketplace": "amazon", "monthly_searches": 52400,  "cpc": Decimal("1.18"), "competition_level": "medium", "difficulty_score": Decimal("55.0"), "opportunity_score": Decimal("74.0"), "intent": "purchase"},
    {"keyword": "non slip kitchen mat set",          "marketplace": "amazon", "monthly_searches": 41800,  "cpc": Decimal("0.76"), "competition_level": "low",    "difficulty_score": Decimal("32.0"), "opportunity_score": Decimal("88.0"), "intent": "purchase"},
    {"keyword": "bamboo cutting board set",          "marketplace": "amazon", "monthly_searches": 98500,  "cpc": Decimal("0.88"), "competition_level": "medium", "difficulty_score": Decimal("51.0"), "opportunity_score": Decimal("76.0"), "intent": "purchase"},
    {"keyword": "resistance bands home workout",     "marketplace": "amazon", "monthly_searches": 187000, "cpc": Decimal("1.05"), "competition_level": "high",   "difficulty_score": Decimal("71.0"), "opportunity_score": Decimal("69.0"), "intent": "purchase"},
    {"keyword": "cable management box desk",         "marketplace": "amazon", "monthly_searches": 29300,  "cpc": Decimal("0.92"), "competition_level": "low",    "difficulty_score": Decimal("29.0"), "opportunity_score": Decimal("91.0"), "intent": "purchase"},
    {"keyword": "phone stand for desk adjustable",   "marketplace": "amazon", "monthly_searches": 63100,  "cpc": Decimal("0.61"), "competition_level": "high",   "difficulty_score": Decimal("78.0"), "opportunity_score": Decimal("57.0"), "intent": "purchase"},
    {"keyword": "lumbar support back cushion",       "marketplace": "amazon", "monthly_searches": 44700,  "cpc": Decimal("1.31"), "competition_level": "medium", "difficulty_score": Decimal("46.0"), "opportunity_score": Decimal("80.0"), "intent": "purchase"},
    {"keyword": "BPA free water bottle stainless",   "marketplace": "amazon", "monthly_searches": 88200,  "cpc": Decimal("1.12"), "competition_level": "high",   "difficulty_score": Decimal("62.0"), "opportunity_score": Decimal("73.0"), "intent": "purchase"},
]


# ── Helpers ───────────────────────────────────────────────────────────
def _ok(msg):   print(f"  \033[32m✓\033[0m {msg}")
def _skip(msg): print(f"  \033[33m→\033[0m {msg} (already exists, skipped)")
def _info(msg): print(f"  \033[36m·\033[0m {msg}")


async def seed_plans(db: AsyncSession) -> dict:
    """Seed subscription plans. Returns {name: plan_id} mapping."""
    from app.models.tenant import Plan
    plan_ids = {}
    for p in PLAN_DATA:
        existing = await db.scalar(select(Plan).where(Plan.name == p["name"]))
        if existing:
            _skip(f"Plan: {p['name']}")
            plan_ids[p["name"]] = existing.id
        else:
            plan = Plan(
                name=p["name"],
                price_monthly=p["price_monthly"],
                price_annual=p["price_annual"],
                limits=p["limits"],
                features=p["features"],
                is_active=True,
            )
            db.add(plan)
            await db.flush()
            _ok(f"Plan: {p['name']}  (${p['price_monthly']}/mo)")
            plan_ids[p["name"]] = plan.id
    await db.commit()
    return plan_ids


async def seed_dev_tenant(db: AsyncSession, plan_ids: dict) -> None:
    """Seed the dev tenant and user used by the auth bypass (ENVIRONMENT != production)."""
    from app.models.tenant import Tenant, TenantMember
    from app.models.user import User
    import uuid

    pro_plan_id = plan_ids.get("Professional")

    # Tenant
    existing_tenant = await db.scalar(select(Tenant).where(Tenant.id == uuid.UUID(DEV_TENANT_ID)))
    if existing_tenant:
        _skip(f"Dev tenant ({DEV_TENANT_SLUG})")
    else:
        trial_end = datetime.now(timezone.utc) + timedelta(days=14)
        tenant = Tenant(
            id=uuid.UUID(DEV_TENANT_ID),
            slug=DEV_TENANT_SLUG,
            name="Demo Seller Co.",
            plan_id=pro_plan_id,
            trial_ends_at=trial_end,
            is_active=True,
            settings={"onboarding_complete": False},
        )
        db.add(tenant)
        await db.flush()
        _ok(f"Dev tenant: {DEV_TENANT_SLUG} (id={DEV_TENANT_ID})")

    # User
    existing_user = await db.scalar(select(User).where(User.id == uuid.UUID(DEV_USER_ID)))
    if existing_user:
        _skip(f"Dev user ({DEV_USER_EMAIL})")
    else:
        user = User(
            id=uuid.UUID(DEV_USER_ID),
            clerk_id="dev_bypass_user",
            email=DEV_USER_EMAIL,
            full_name="Dev Seller",
            is_active=True,
        )
        db.add(user)
        await db.flush()
        _ok(f"Dev user: {DEV_USER_EMAIL}")

    # Membership
    existing_member = await db.scalar(
        select(TenantMember).where(
            TenantMember.tenant_id == uuid.UUID(DEV_TENANT_ID),
            TenantMember.user_id == uuid.UUID(DEV_USER_ID),
        )
    )
    if existing_member:
        _skip("Dev tenant membership")
    else:
        member = TenantMember(
            tenant_id=uuid.UUID(DEV_TENANT_ID),
            user_id=uuid.UUID(DEV_USER_ID),
            role="owner",
            permissions={"all": True},
        )
        db.add(member)
        _ok("Dev tenant membership: owner")

    await db.commit()


async def seed_products(db: AsyncSession) -> list:
    """Seed demo products. Returns list of product IDs."""
    from app.models.product import Product

    product_ids = []
    for p in PRODUCTS:
        existing = await db.scalar(
            select(Product).where(Product.asin == p["asin"])
        )
        if existing:
            _skip(f"Product: {p['asin']} — {p['title'][:50]}")
            product_ids.append(existing.id)
        else:
            product = Product(**{k: v for k, v in p.items()})
            db.add(product)
            await db.flush()
            _ok(f"Product: {p['asin']} — {p['title'][:50]}")
            product_ids.append(product.id)

    await db.commit()
    return product_ids


async def seed_keywords(db: AsyncSession) -> None:
    """Seed demo keywords."""
    from app.models.keyword import Keyword

    for kw in KEYWORDS:
        existing = await db.scalar(
            select(Keyword).where(
                Keyword.keyword == kw["keyword"],
                Keyword.marketplace == kw["marketplace"],
            )
        )
        if existing:
            _skip(f"Keyword: {kw['keyword'][:45]}")
        else:
            keyword = Keyword(**kw)
            db.add(keyword)
            _ok(f"Keyword: {kw['keyword'][:45]}")

    await db.commit()


async def seed_inventory(db: AsyncSession, product_ids: list) -> None:
    """Seed a demo FBA warehouse + inventory for dev tenant products."""
    from app.models.inventory import Warehouse, Inventory
    from datetime import date

    # Warehouse
    existing_wh = await db.scalar(
        select(Warehouse).where(Warehouse.name == "Demo FBA — US East")
    )
    if existing_wh:
        _skip("Warehouse: Demo FBA — US East")
        warehouse_id = existing_wh.id
    else:
        wh = Warehouse(
            name="Demo FBA — US East",
            type="fba",
            country_code="US",
            marketplace_codes=["amazon"],
            address={"city": "Hebron", "state": "KY", "country": "US"},
            active=True,
        )
        db.add(wh)
        await db.flush()
        _ok("Warehouse: Demo FBA — US East")
        warehouse_id = wh.id

    STOCK = [412, 287, 55, 198, 14, 321, 176, 89]  # qty per product (14 = low stock alert)
    REORDER = [100, 75, 100, 80, 50, 100, 80, 60]
    COSTS = [8.50, 6.20, 11.00, 4.30, 7.80, 7.10, 4.60, 2.90]

    today = date.today()
    for i, product_id in enumerate(product_ids):
        existing_inv = await db.scalar(
            select(Inventory).where(
                Inventory.product_id == product_id,
                Inventory.warehouse_id == warehouse_id,
            )
        )
        if existing_inv:
            _skip(f"Inventory row #{i+1}")
            continue

        qty = STOCK[i] if i < len(STOCK) else 100
        reorder_pt = REORDER[i] if i < len(REORDER) else 50
        cost = Decimal(str(COSTS[i])) if i < len(COSTS) else Decimal("5.00")

        # Estimate a stockout date based on ~10 units/day burn rate
        burn_rate = 10
        days_left = max(qty // burn_rate, 1)
        stockout_date = today + timedelta(days=days_left)

        inv = Inventory(
            product_id=product_id,
            warehouse_id=warehouse_id,
            marketplace="amazon",
            sku=f"SV-DEMO-{1001 + i}",
            fnsku=f"X00{1001 + i}DEMO",
            quantity_on_hand=qty,
            quantity_reserved=max(qty // 20, 1),
            quantity_inbound=50,
            reorder_point=reorder_pt,
            reorder_quantity=reorder_pt * 2,
            lead_time_days=28,
            unit_cost=cost,
            stockout_date=stockout_date,
            overstock_risk=(qty > reorder_pt * 6),
            last_order_date=today - timedelta(days=30),
        )
        db.add(inv)
        _ok(f"Inventory row #{i+1}: {qty} units, stockout ~{days_left}d")

    await db.commit()


# ── Main ──────────────────────────────────────────────────────────────
async def run(plans_only: bool = False):
    # Import settings after path is set
    from app.core.config import settings

    db_url = os.environ.get("DATABASE_URL") or settings.DATABASE_URL
    if not db_url:
        print("ERROR: DATABASE_URL not set")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"  SellerVision AI — Database Seed")
    print(f"  DB: {db_url.split('@')[-1] if '@' in db_url else db_url}")
    print(f"{'='*60}\n")

    engine = create_async_engine(db_url, echo=False)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as db:
        print("── Plans ──────────────────────────────────────────────")
        plan_ids = await seed_plans(db)

        if plans_only:
            print("\nDone (--plans-only mode).")
            await engine.dispose()
            return

        print("\n── Dev tenant & user ──────────────────────────────────")
        await seed_dev_tenant(db, plan_ids)

        print("\n── Products ───────────────────────────────────────────")
        product_ids = await seed_products(db)

        print("\n── Keywords ───────────────────────────────────────────")
        await seed_keywords(db)

        print("\n── Inventory ──────────────────────────────────────────")
        await seed_inventory(db, product_ids)

    await engine.dispose()

    print(f"\n{'='*60}")
    print(f"  Seed complete!")
    print(f"  Dev tenant:  {DEV_TENANT_SLUG} ({DEV_TENANT_ID})")
    print(f"  Dev user:    {DEV_USER_EMAIL} ({DEV_USER_ID})")
    print(f"  Products:    {len(product_ids)} seeded")
    print(f"  Keywords:    {len(KEYWORDS)} seeded")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--plans-only", action="store_true",
                        help="Only seed Plans table (safe for production)")
    args = parser.parse_args()
    asyncio.run(run(plans_only=args.plans_only))
