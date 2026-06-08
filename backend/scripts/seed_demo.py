"""
Seed demo data: plans, a demo tenant, demo user, sample products.
Run: python scripts/seed_demo.py
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

os.environ.setdefault("OPENAI_API_KEY", "placeholder")
os.environ.setdefault("ANTHROPIC_API_KEY", "placeholder")

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from app.core.config import settings


async def seed():
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        # Plans
        print("Seeding plans...")
        await db.execute(text("""
            INSERT INTO public.plans (name, price_monthly, price_annual, limits, features, is_active)
            VALUES
              ('Starter',      49,   470, '{"products":25,"keywords":500,"api_calls":10000}'::jsonb,
               '{"ai_scoring":true,"basic_analytics":true}'::jsonb, true),
              ('Professional', 149, 1430, '{"products":100,"keywords":5000,"api_calls":100000}'::jsonb,
               '{"ai_scoring":true,"advanced_analytics":true,"ppc_optimizer":true,"digital_twin":true}'::jsonb, true),
              ('Business',     299, 2870, '{"products":500,"keywords":25000,"api_calls":500000}'::jsonb,
               '{"ai_scoring":true,"advanced_analytics":true,"ppc_optimizer":true,"digital_twin":true,"agency_tools":true,"white_label":true}'::jsonb, true),
              ('Agency',       599, 5750, '{"products":-1,"keywords":-1,"api_calls":-1}'::jsonb,
               '{"everything":true}'::jsonb, true)
            ON CONFLICT DO NOTHING
        """))

        # Demo user
        print("Seeding demo user...")
        await db.execute(text("""
            INSERT INTO public.users (email, full_name, clerk_id, is_active)
            VALUES ('demo@sellervision.ai', 'Demo User', 'user_demo_001', true)
            ON CONFLICT (email) DO NOTHING
        """))

        # Demo tenant
        print("Seeding demo tenant...")
        await db.execute(text("""
            INSERT INTO public.tenants (slug, name, plan_id, is_active)
            SELECT 'demo', 'Demo Store', id, true
            FROM public.plans WHERE name = 'Professional'
            ON CONFLICT (slug) DO NOTHING
        """))

        # Link demo user to demo tenant
        await db.execute(text("""
            INSERT INTO public.tenant_members (tenant_id, user_id, role)
            SELECT t.id, u.id, 'owner'
            FROM public.tenants t, public.users u
            WHERE t.slug = 'demo' AND u.email = 'demo@sellervision.ai'
            ON CONFLICT DO NOTHING
        """))

        # Sample products
        print("Seeding sample products...")
        await db.execute(text("""
            INSERT INTO products (asin, title, brand, category, marketplace, current_price, cost,
                                  opportunity_score, risk_score, profit_score, is_tracked, is_own_product)
            VALUES
              ('B08N5WRWNW', 'Premium Bamboo Cutting Board Set', 'EcoChef', 'Kitchen', 'amazon',
               34.99, 8.50, 82.5, 25.0, 78.0, true, true),
              ('B09K3RJFLT', 'Silicone Cooking Utensil Set 12pc', 'ChefMaster', 'Kitchen', 'amazon',
               27.99, 6.20, 74.0, 32.0, 71.0, true, true),
              ('B07XJ8C8F5', 'LED Desk Lamp with USB Charging', 'LuminTech', 'Electronics', 'amazon',
               45.99, 11.00, 68.0, 41.0, 63.0, true, false),
              ('B09BQXLDMK', 'Resistance Bands Set Heavy Duty', 'FitPro', 'Sports', 'amazon',
               22.99, 4.80, 91.0, 18.0, 88.0, true, false),
              ('B08FWZD4LX', 'Stainless Steel Water Bottle 32oz', 'HydroFlow', 'Sports', 'amazon',
               19.99, 4.20, 65.0, 48.0, 60.0, false, false)
            ON CONFLICT DO NOTHING
        """))

        # Sample PPC campaigns
        print("Seeding sample PPC campaigns...")
        await db.execute(text("""
            INSERT INTO ppc_campaigns (product_id, marketplace, name, type, status,
                                       daily_budget, spend_today, impressions, clicks,
                                       orders, revenue, acos, roas, tacos)
            SELECT p.id, 'amazon',
                   p.title || ' - Auto Campaign',
                   'auto', 'enabled',
                   25.00, 18.43, 4820, 124, 8, 279.92, 22.5, 4.44, 9.8
            FROM products p WHERE p.asin = 'B08N5WRWNW'
            ON CONFLICT DO NOTHING
        """))

        # Sample keywords
        print("Seeding sample keywords...")
        await db.execute(text("""
            INSERT INTO keywords (keyword, marketplace, monthly_searches, cpc,
                                  competition_level, difficulty_score, opportunity_score,
                                  ppc_score, seo_score, intent)
            VALUES
              ('bamboo cutting board', 'amazon', 185000, 1.24, 'medium', 52.0, 78.0, 71.0, 74.0, 'buy'),
              ('silicone cooking utensils', 'amazon', 74000, 0.98, 'medium', 45.0, 82.0, 79.0, 81.0, 'buy'),
              ('led desk lamp usb', 'amazon', 48000, 1.67, 'high', 68.0, 61.0, 58.0, 62.0, 'buy'),
              ('resistance bands set', 'amazon', 320000, 1.43, 'high', 71.0, 85.0, 77.0, 80.0, 'buy'),
              ('stainless steel water bottle', 'amazon', 550000, 1.89, 'high', 79.0, 59.0, 54.0, 56.0, 'buy')
            ON CONFLICT DO NOTHING
        """))

        # Sample inventory
        print("Seeding sample inventory...")
        await db.execute(text("""
            INSERT INTO inventory (product_id, marketplace, sku, quantity_on_hand,
                                   quantity_reserved, quantity_inbound, reorder_point,
                                   reorder_quantity, unit_cost, lead_time_days)
            SELECT p.id, 'amazon',
                   'SV-' || p.asin,
                   CASE p.asin
                     WHEN 'B08N5WRWNW' THEN 342
                     WHEN 'B09K3RJFLT' THEN 187
                     WHEN 'B07XJ8C8F5' THEN 89
                     WHEN 'B09BQXLDMK' THEN 512
                     WHEN 'B08FWZD4LX' THEN 43
                   END,
                   0, 200, 100, 300, p.cost, 28
            FROM products p
            ON CONFLICT DO NOTHING
        """))

        await db.commit()
        print("\nSeed complete!")
        print("  Plans: Starter / Professional / Business / Agency")
        print("  Tenant: demo (slug='demo')")
        print("  User: demo@sellervision.ai")
        print("  Products: 5 sample ASINs")
        print("  Keywords: 5 high-volume terms")
        print("  Inventory: stocked for all 5 products")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
