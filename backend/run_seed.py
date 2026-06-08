#!/usr/bin/env python3
"""
SellerVision AI — Demo Data Seeder
Run: python run_seed.py
"""
import psycopg2
from psycopg2.extras import execute_values
import json
import sys

DSN = dict(host="localhost", port=5432,
           dbname="sellervision", user="sellervision", password="sellervision")

USER_ID     = "8e63fa3b-4d49-4943-aeb7-ebf1b41e4825"  # dev user
TENANT_ID   = "c978f4a3-ec4c-434c-b484-cb264f963624"
WAREHOUSE_ID = "aaaa0001-0000-0000-0000-000000000001"

def run():
    conn = psycopg2.connect(**DSN)
    conn.autocommit = False
    cur = conn.cursor()

    # ── 1. PRODUCTS ───────────────────────────────────────────────
    products = [
        # (id, asin, title, brand, category, subcategory, marketplace,
        #  current_price, buy_box_price, cost, weight_lbs,
        #  is_tracked, is_own_product,
        #  opportunity_score, risk_score, profit_score, competition_score, market_entry_score,
        #  tags)
        ("11000001-0000-0000-0000-000000000001","B08N5WRWNW",
         "Bamboo Cutting Board Set (3-Pack)","EcoKitchen",
         "Home & Kitchen","Cutting Boards","amazon",
         34.99,34.99,8.50,2.1,True,True,87,24,81,42,79,
         ["eco","bamboo","kitchen","bestseller"]),
        ("11000001-0000-0000-0000-000000000002","B09G3HRMVQ",
         "Stainless Steel Meal Prep Containers (7-Pack)","PrepMaster",
         "Home & Kitchen","Food Storage","amazon",
         28.99,27.99,6.20,1.8,True,True,83,31,78,55,74,
         ["meal-prep","containers","bpa-free"]),
        ("11000001-0000-0000-0000-000000000003","B0CKXYZABC",
         "Resistance Band Set (11 Piece)","FitCore",
         "Sports & Outdoors","Exercise Bands","amazon",
         24.99,24.99,4.80,0.9,True,True,91,19,85,38,88,
         ["fitness","resistance-bands","home-gym","trending"]),
        ("11000001-0000-0000-0000-000000000004","B07XYZDEF1",
         "LED Desk Lamp with USB Charging Port","LumiWork",
         "Office Products","Desk Lamps","amazon",
         42.99,41.99,11.00,1.4,True,True,79,33,72,61,71,
         ["office","lamp","usb","productivity"]),
        ("11000001-0000-0000-0000-000000000005","B0BXYZ1234",
         "Silicone Reusable Bags (10-Pack)","GreenSeal",
         "Home & Kitchen","Storage Bags","amazon",
         19.99,19.99,4.10,0.5,True,True,88,22,82,44,84,
         ["eco","silicone","reusable","zero-waste"]),
        ("11000001-0000-0000-0000-000000000006","B0CXYZ5678",
         "Foam Roller for Deep Tissue Massage","RecoverPro",
         "Sports & Outdoors","Recovery Equipment","amazon",
         29.99,29.99,7.50,1.2,True,False,76,28,71,52,68,
         ["recovery","foam-roller","fitness","massage"]),
        ("11000001-0000-0000-0000-000000000007","B0DXYZ9012",
         "Portable Phone Stand Adjustable","TechDesk",
         "Electronics","Phone Accessories","amazon",
         15.99,15.49,3.20,0.3,True,False,72,41,68,67,65,
         ["phone","stand","desk","adjustable"]),
        ("11000001-0000-0000-0000-000000000008","B0EXYZ3456",
         "Digital Kitchen Scale (11 lb)","PrecisionPro",
         "Home & Kitchen","Kitchen Scales","amazon",
         22.99,22.99,5.80,0.8,True,True,80,27,75,49,77,
         ["kitchen","scale","baking","precision"]),
        ("11000001-0000-0000-0000-000000000009","B0FXYZ7890",
         "Insulated Water Bottle 32oz","HydroVault",
         "Sports & Outdoors","Water Bottles","amazon",
         32.99,31.99,8.00,1.1,True,True,85,26,79,48,81,
         ["hydration","insulated","stainless","eco"]),
        ("11000001-0000-0000-0000-000000000010","B0GXYZ1234",
         "Essential Oil Diffuser 500ml","AromaZen",
         "Health & Beauty","Diffusers","amazon",
         38.99,37.99,9.50,1.6,True,True,82,30,77,53,76,
         ["aromatherapy","diffuser","wellness","home"]),
        ("11000001-0000-0000-0000-000000000011",None,
         "Collapsible Silicone Food Storage Bowls","FlexStore",
         "Kitchen","Food Storage","walmart",
         16.99,16.99,3.80,0.6,True,True,78,35,73,58,70,
         ["walmart","silicone","storage","collapsible"]),
        ("11000001-0000-0000-0000-000000000012",None,
         "Non-Slip Yoga Mat Extra Thick 6mm","ZenFlow",
         "Sports","Yoga","walmart",
         27.99,27.99,6.90,2.3,True,True,81,29,76,51,75,
         ["yoga","mat","fitness","non-slip"]),
        ("11000001-0000-0000-0000-000000000013",None,
         "Natural Beeswax Lip Balm Set (6-Pack)","PureLip",
         "Beauty","Lip Care","shopify",
         18.99,18.99,3.50,0.2,True,True,89,18,84,36,87,
         ["natural","beeswax","lip-balm","organic"]),
        ("11000001-0000-0000-0000-000000000014",None,
         "Hand-Poured Soy Candle Set (3-Pack)","LightHaven",
         "Home Decor","Candles","shopify",
         44.99,44.99,12.00,1.8,True,True,86,21,80,40,83,
         ["soy-candle","handmade","home-decor","gift"]),
        ("11000001-0000-0000-0000-000000000015",None,
         "Viral Mushroom Lamp Night Light","GlowTok",
         "Home Decor","Lighting","tiktok",
         22.99,22.99,5.00,0.7,True,False,93,15,88,31,92,
         ["viral","tiktok","mushroom-lamp","aesthetic","trending"]),
        ("11000001-0000-0000-0000-000000000016",None,
         "Cloud Ice Cream Maker Mini","FrostyTok",
         "Kitchen","Appliances","tiktok",
         34.99,34.99,8.20,1.3,True,False,91,17,86,33,90,
         ["viral","tiktok","ice-cream","trending","summer"]),
        ("11000001-0000-0000-0000-000000000017",None,
         "Personalized Leather Journal A5","CraftedPage",
         "Books & Stationery","Journals","etsy",
         52.00,52.00,14.00,0.9,True,True,84,23,79,43,81,
         ["handmade","leather","personalized","gift","etsy"]),
        ("11000001-0000-0000-0000-000000000018",None,
         "Macramé Wall Hanging Boho Large","BohoWeave",
         "Home Decor","Wall Art","etsy",
         68.00,68.00,18.00,0.6,True,True,82,25,77,45,78,
         ["macrame","boho","handmade","wall-decor","etsy"]),
        ("11000001-0000-0000-0000-000000000019",None,
         "Vintage Film Camera Fully Functional","RetroLens",
         "Electronics","Cameras","ebay",
         89.99,87.99,35.00,1.2,True,False,74,38,69,62,66,
         ["vintage","film-camera","retro","ebay"]),
        ("11000001-0000-0000-0000-000000000020",None,
         "Collectible Enamel Pin Set (10-Pack)","PinCraft",
         "Collectibles","Pins","ebay",
         24.99,24.99,6.50,0.2,True,False,77,32,72,54,72,
         ["enamel-pins","collectibles","art","ebay"]),
    ]
    for p in products:
        cur.execute("""
            INSERT INTO products
              (id, asin, title, brand, category, subcategory, marketplace,
               current_price, buy_box_price, cost, weight_lbs,
               is_tracked, is_own_product,
               opportunity_score, risk_score, profit_score, competition_score, market_entry_score,
               tags,
               created_at, updated_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                    NOW(), NOW())
            ON CONFLICT (id) DO NOTHING
        """, p)
    print(f"  products: {cur.rowcount} inserted (last batch)")

    # ── 2. INVENTORY ──────────────────────────────────────────────
    inventory = [
        # (product_id, sku, qty_on_hand, qty_reserved, qty_inbound,
        #  reorder_point, reorder_quantity, lead_time_days, unit_cost,
        #  stockout_date, overstock_risk, last_order_date)
        ("11000001-0000-0000-0000-000000000001","ECO-BB-001", 342,28,0,  75,200,21,8.50, None,  False,"2026-05-15"),
        ("11000001-0000-0000-0000-000000000002","PMP-SC-002", 187,15,150,60,180,18,6.20, None,  False,"2026-05-20"),
        ("11000001-0000-0000-0000-000000000003","FIT-RB-003",  18, 5,300, 50,250,14,4.80,"2026-06-21",False,"2026-05-01"),
        ("11000001-0000-0000-0000-000000000004","LMW-DL-004",  94, 8,0,  40,120,24,11.00,None,  False,"2026-05-25"),
        ("11000001-0000-0000-0000-000000000005","GRN-SB-005",   8, 2,500, 80,400,16,4.10,"2026-06-14",False,"2026-04-20"),
        ("11000001-0000-0000-0000-000000000008","PRE-KS-008", 156,12,0,  45,150,20,5.80, None,  False,"2026-05-30"),
        ("11000001-0000-0000-0000-000000000009","HYD-WB-009", 412,35,0, 100,300,18,8.00, None,  True, "2026-05-10"),
        ("11000001-0000-0000-0000-000000000010","ARO-ED-010",  67, 6,100, 30,120,22,9.50, None,  False,"2026-05-22"),
        ("11000001-0000-0000-0000-000000000011","WMT-SB-011", 234,18,0,  60,200,19,3.80, None,  False,"2026-05-18"),
        ("11000001-0000-0000-0000-000000000012","WMT-YM-012",   5, 1,200, 40,150,21,6.90,"2026-06-18",False,"2026-04-15"),
        ("11000001-0000-0000-0000-000000000013","SHO-LB-013",  89, 7,0,  25,100,10,3.50, None,  False,"2026-05-28"),
        ("11000001-0000-0000-0000-000000000014","SHO-SC-014",  45, 3,0,  20, 80,14,12.00,None,  False,"2026-05-20"),
        ("11000001-0000-0000-0000-000000000015","TTK-ML-015",   3, 0,500,100,600,14,5.00,"2026-06-10",False,"2026-04-01"),
        ("11000001-0000-0000-0000-000000000016","TTK-IC-016",  72, 9,150, 50,200,14,8.20, None,  False,"2026-05-25"),
        ("11000001-0000-0000-0000-000000000017","ETY-LJ-017",  28, 2,0,  10, 50,21,14.00,None,  False,"2026-05-15"),
    ]
    # Get existing product_ids to avoid FK violations
    cur.execute("SELECT id FROM products")
    existing_products = {str(r[0]) for r in cur.fetchall()}

    inv_inserted = 0
    for inv in inventory:
        product_id = inv[0]
        if product_id not in existing_products:
            print(f"  SKIP inventory for {product_id} — product not found")
            continue
        cur.execute("""
            INSERT INTO inventory
              (id, product_id, warehouse_id, marketplace, sku,
               quantity_on_hand, quantity_reserved, quantity_inbound,
               reorder_point, reorder_quantity, lead_time_days, unit_cost,
               stockout_date, overstock_risk, last_order_date,
               created_at, updated_at)
            VALUES (gen_random_uuid(), %s, %s,
                    (SELECT marketplace FROM products WHERE id=%s),
                    %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s, NOW(), NOW())
        """, (product_id, WAREHOUSE_ID, product_id,
              inv[1], inv[2], inv[3], inv[4], inv[5], inv[6], inv[7], inv[8],
              inv[9], inv[10], inv[11]))
        inv_inserted += 1
    print(f"  inventory: {inv_inserted} inserted")

    # ── 3. KEYWORDS ───────────────────────────────────────────────
    keywords = [
        # (keyword, marketplace, monthly_searches, search_volume_trend, cpc,
        #  competition_level, difficulty_score, opportunity_score, ppc_score, seo_score,
        #  intent, related_keywords)
        ("bamboo cutting board","amazon",48200,8.2,1.24,"medium",42,87,79,84,"commercial",["cutting board set","bamboo kitchen","wood cutting board"]),
        ("meal prep containers","amazon",124000,12.5,0.98,"high",58,83,71,76,"commercial",["food storage containers","glass meal prep","bpa free containers"]),
        ("resistance bands set","amazon",218000,22.1,0.87,"high",61,91,68,73,"commercial",["exercise bands","workout bands","resistance loops"]),
        ("led desk lamp usb","amazon",67400,5.4,1.56,"medium",49,79,82,78,"commercial",["usb desk lamp","office lamp","led lamp with usb port"]),
        ("silicone reusable bags","amazon",84300,18.7,0.76,"medium",38,88,74,81,"commercial",["reusable storage bags","silicone food bags","eco bags"]),
        ("foam roller exercise","amazon",142000,9.3,1.12,"high",55,76,73,70,"commercial",["foam roller massage","deep tissue roller","muscle roller"]),
        ("insulated water bottle","amazon",396000,14.2,1.43,"high",69,85,66,71,"commercial",["32oz water bottle","stainless steel bottle","hydro flask"]),
        ("essential oil diffuser","amazon",187000,7.8,1.31,"high",62,82,77,74,"commercial",["aromatherapy diffuser","oil diffuser 500ml","ultrasonic diffuser"]),
        ("kitchen scale digital","amazon",93000,6.1,0.89,"medium",44,80,80,77,"commercial",["food scale","baking scale","digital food scale"]),
        ("yoga mat thick","amazon",211000,11.9,1.07,"high",57,81,69,72,"commercial",["6mm yoga mat","exercise mat","non slip yoga mat"]),
        ("mushroom lamp led","tiktok",312000,89.4,0.43,"low",18,93,91,95,"commercial",["mushroom night light","aesthetic lamp","room decor light"]),
        ("ice cream maker mini","tiktok",178000,67.2,0.38,"low",14,91,93,96,"commercial",["mini ice cream machine","ice cream at home","cloud ice cream"]),
        ("soy candle handmade","shopify",56000,24.8,1.68,"low",22,86,84,88,"commercial",["hand poured candle","natural candle","soy wax candle"]),
        ("lip balm natural organic","shopify",42000,19.3,1.22,"medium",31,89,80,85,"commercial",["beeswax lip balm","organic lip balm","natural lip care"]),
        ("leather journal personalized","etsy",38000,16.7,2.14,"low",27,84,82,87,"commercial",["custom journal","leather notebook","personalized notebook"]),
        ("macrame wall hanging","etsy",64000,21.4,1.89,"medium",33,82,79,84,"commercial",["boho wall decor","macrame decor","wall hanging art"]),
        ("best meal prep containers glass","amazon",28000,31.2,1.34,"low",29,92,86,89,"informational",["glass containers with lids","meal prep glass","microwave safe containers"]),
        ("home gym equipment set","amazon",144000,28.9,1.61,"high",64,88,72,68,"commercial",["home workout equipment","gym equipment bundle","exercise equipment"]),
        ("eco friendly kitchen products","amazon",52000,34.7,0.92,"low",24,90,83,88,"commercial",["sustainable kitchen","eco kitchen","green kitchen products"]),
        ("portable charger fast charging","amazon",287000,6.8,1.48,"high",71,77,74,70,"commercial",["power bank","portable battery","fast charging power bank"]),
    ]
    kw_inserted = 0
    for kw in keywords:
        cur.execute("""
            INSERT INTO keywords
              (id, keyword, marketplace, monthly_searches, search_volume_trend,
               cpc, competition_level, difficulty_score, opportunity_score,
               ppc_score, seo_score, intent, related_keywords,
               created_at, updated_at, last_updated)
            VALUES (gen_random_uuid(),%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                    NOW(), NOW(), NOW())
        """, kw)
        kw_inserted += 1
    print(f"  keywords: {kw_inserted} inserted")

    # ── 4. LISTINGS ───────────────────────────────────────────────
    listings = [
        # (product_id, marketplace, title, bullet_points, description, backend_keywords,
        #  price, status, seo_score, completeness_score, ai_generated)
        ("11000001-0000-0000-0000-000000000001","amazon",
         "EcoKitchen Bamboo Cutting Board Set of 3 - Organic, Eco-Friendly, Juice Groove Design",
         ["SET OF 3 SIZES: Small 9x6, Medium 12x8, Large 15x11 for every cutting task",
          "PREMIUM BAMBOO: Harder than maple, knife-friendly, naturally antimicrobial surface",
          "JUICE GROOVES: Deep channels prevent messy countertops during meat and fruit prep",
          "EASY CLEAN: Hand wash only, apply mineral oil monthly to extend lifespan by years",
          "SUSTAINABLE: 100% organic Moso bamboo, FSC certified, plastic-free packaging"],
         "Transform your kitchen prep with the EcoKitchen Bamboo Cutting Board Set.",
         ["bamboo","cutting board","organic","kitchen","eco-friendly","wood board"],
         34.99,"active",94,96,True),
        ("11000001-0000-0000-0000-000000000003","amazon",
         "FitCore Resistance Band Set 11 Piece - Home Gym Workout Bands for Men and Women",
         ["11-PIECE COMPLETE SET: 5 resistance levels 10-50 lbs, handles, ankle straps, door anchor and carry bag",
          "NATURAL LATEX: Premium elastic latex resists snapping, maintains tension through 10,000 plus uses",
          "FULL BODY WORKOUT: Glutes, arms, back, legs, shoulders — 40 plus exercises in one kit",
          "NON-SLIP HANDLES: Padded foam grips prevent hand fatigue during long sessions",
          "LIFETIME WARRANTY: We stand behind every band with a no-questions-asked replacement policy"],
         "Get a complete gym in your living room with the FitCore 11-Piece Resistance Band Set.",
         ["resistance bands","workout","home gym","exercise bands","strength training","fitness"],
         24.99,"active",97,98,True),
        ("11000001-0000-0000-0000-000000000005","amazon",
         "GreenSeal Reusable Silicone Food Storage Bags 10-Pack - Freezer Microwave Dishwasher Safe",
         ["10-PACK VALUE: 4 sandwich, 3 snack, 2 gallon, 1 stand-up pouch sizes for every need",
          "FOOD GRADE SILICONE: BPA-free, PVC-free, phthalate-free — safe for all foods",
          "LEAKPROOF SEAL: Dual-lock zipper holds tight even in the freezer",
          "SAVES MONEY: Replace 1,000 plus single-use plastic bags per year",
          "ECO CERTIFIED: B-Corp certified manufacturer, carbon neutral shipping"],
         "Make the switch to sustainable storage with GreenSeal Reusable Silicone Bags.",
         ["silicone bags","reusable","eco-friendly","food storage","freezer bags","sustainable"],
         19.99,"active",96,97,True),
        ("11000001-0000-0000-0000-000000000009","amazon",
         "HydroVault 32oz Insulated Water Bottle - 24hr Cold 12hr Hot Leak-Proof BPA-Free",
         ["DOUBLE-WALL VACUUM INSULATION: Drinks stay cold 24 hours, hot 12 hours — proven in extreme temps",
          "LEAKPROOF LID: Wide mouth with secure locking lid, no spills in your bag",
          "PREMIUM 18/8 STAINLESS: Will not rust, retain odors, or leach chemicals",
          "32OZ CAPACITY: Perfect for all-day hydration at the gym, office, or trail",
          "LIFETIME GUARANTEE: One-time free replacement, no receipts needed"],
         "Stay hydrated all day with the HydroVault 32oz Insulated Bottle.",
         ["water bottle","insulated","stainless steel","32oz","hydro","leak proof","BPA free"],
         32.99,"active",95,96,True),
        ("11000001-0000-0000-0000-000000000015","tiktok",
         "Mushroom Night Light LED Color Changing - Aesthetic Room Decor Lamp for Bedroom",
         ["16 COLOR MODES: Cycle through rainbow colors or lock your favorite with remote control",
          "SOFT WARM GLOW: Eye-safe 3000K warm white for sleep-friendly ambient lighting",
          "TOUCH AND REMOTE: Switch modes by touch or included remote from across the room",
          "USB POWERED: Works with any USB-A charger, phone brick, or power bank",
          "VIRAL GIFT PICK: Number 1 trending bedroom decor on TikTok — perfect gift for teens"],
         "Create magical bedroom vibes with the GlowTok Mushroom Night Light.",
         ["mushroom lamp","night light","LED","room decor","aesthetic","color changing","tiktok"],
         22.99,"active",98,99,True),
        ("11000001-0000-0000-0000-000000000013","shopify",
         "Natural Beeswax Lip Balm Set 6-Pack Organic Flavors Moisturizing SPF 15",
         ["6 FLAVOR VARIETY: Honey, Vanilla, Cherry, Peppermint, Coconut and Unscented",
          "100% NATURAL: Beeswax, shea butter, vitamin E — no parabens, no petroleum",
          "SPF 15 PROTECTION: Broad-spectrum UVA/UVB protection in every stick",
          "LONG-LASTING MOISTURE: Clinically tested for 8-hour hydration",
          "ECO PACKAGING: Biodegradable tubes, recyclable box, cruelty-free certified"],
         "Treat your lips to pure nature with PureLip Beeswax Lip Balm Set.",
         ["lip balm","beeswax","natural","organic","SPF","moisturizing","lip care"],
         18.99,"active",93,95,True),
        ("11000001-0000-0000-0000-000000000010","amazon",
         "AromaZen Essential Oil Diffuser 500ml - Ultrasonic 7 LED Colors Auto Shut-Off Quiet",
         ["LARGE 500ML TANK: Run up to 10 hours on one fill — covers rooms up to 400 sq ft",
          "WHISPER-QUIET: Ultrasonic technology, under 30dB — will not disturb sleep or focus",
          "7 LED MOODS: Warm amber, cool white, or cycle through 7 colors",
          "AUTO SHUT-OFF: Safely powers down when water runs out — no babysitting required",
          "WORKS WITH ALL OILS: Compatible with any brand of essential oil"],
         "Elevate your space with the AromaZen 500ml Ultrasonic Oil Diffuser.",
         ["essential oil diffuser","aromatherapy","ultrasonic","500ml","humidifier","oil diffuser"],
         38.99,"active",94,96,True),
        ("11000001-0000-0000-0000-000000000002","amazon",
         "PrepMaster Meal Prep Containers 7-Pack - Airtight Microwave Safe BPA-Free Portion Control",
         ["7-PACK SET: 3x28oz, 2x20oz, 2x10oz — perfect for breakfast, lunch, dinner and snacks",
          "LEAK-PROOF LID: Snap-lock tabs create an airtight seal, safe to pack in any bag",
          "MICROWAVE AND DISHWASHER SAFE: Eat straight from the container, clean in seconds",
          "PORTION CONTROL: Divided compartments keep proteins, carbs, veggies separate",
          "BPA-FREE TRITAN: Crystal clear, food-safe, will not stain or absorb odors"],
         "Crush your meal prep game with PrepMaster 7-Pack Containers.",
         ["meal prep containers","food storage","airtight","portion control","BPA free","microwave safe"],
         28.99,"active",92,94,True),
        ("11000001-0000-0000-0000-000000000014","shopify",
         "Hand-Poured Soy Candle Set 3-Pack - Natural Fragrance Gift Set",
         ["ALL-NATURAL SOY WAX: Clean burn, no petroleum, no toxins — safe for kids and pets",
          "HAND-POURED: Each candle crafted in small batches for consistent quality",
          "3 SIGNATURE SCENTS: Vanilla Amber, Fresh Linen, and Eucalyptus Mint",
          "LONG BURN TIME: Each 8oz candle burns 45-50 hours",
          "PREMIUM GIFT BOX: Beautiful kraft box with ribbon — ready to gift"],
         "Fill your home with warmth and fragrance with LightHaven Soy Candle Set.",
         ["soy candle","hand-poured","natural","gift set","fragrance","home decor"],
         44.99,"active",91,93,True),
        ("11000001-0000-0000-0000-000000000016","tiktok",
         "Cloud Ice Cream Maker Mini - Viral TikTok Kitchen Gadget Makes Ice Cream in 1 Minute",
         ["MAKES ICE CREAM IN 60 SECONDS: Just freeze the bowl, add ingredients, roll and enjoy",
          "NO MACHINE NEEDED: Completely manual — no electricity, no mess, no waiting",
          "WORKS WITH ANY MILK: Dairy, oat, almond, coconut — all work perfectly",
          "EASY CLEAN: Non-stick inner surface, rinse and store in 30 seconds",
          "VIRAL TIKTOK HIT: Millions of views — try every flavor and go wild"],
         "Make homemade ice cream in 60 seconds flat with the FrostyTok Mini Ice Cream Maker.",
         ["ice cream maker","mini","kitchen gadget","tiktok","viral","homemade ice cream"],
         34.99,"active",96,98,True),
    ]
    lst_inserted = 0
    for lst in listings:
        product_id = lst[0]
        if product_id not in existing_products:
            print(f"  SKIP listing for {product_id} — product not found")
            continue
        cur.execute("""
            INSERT INTO listings
              (id, product_id, marketplace, title, bullet_points, description,
               backend_keywords, price, status, seo_score, completeness_score,
               ai_generated, published_at, created_at, updated_at)
            VALUES (gen_random_uuid(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, NOW(), NOW(), NOW())
        """, (product_id, lst[1], lst[2], lst[3], lst[4], lst[5], lst[6],
              lst[7], lst[8], lst[9], lst[10]))
        lst_inserted += 1
    print(f"  listings: {lst_inserted} inserted")

    # ── 5. MARKETPLACE ASSETS ─────────────────────────────────────
    assets = [
        # (type, name, description, price, downloads, rating, rating_count, tags)
        ("keyword_list","Top 500 Amazon FBA Keywords 2026 Q2",
         "Curated list of 500 high-opportunity keywords across 12 categories. Includes search volume, CPC, competition scores and trend data. Updated quarterly.",
         29.99,847,4.8,142,["keywords","amazon","fba","research"]),
        ("template","AI Listing Template Pack — 20 Niche Templates",
         "High-converting listing templates for 20 popular niches. Each includes title formula, 5 bullet points, A+ content outline. Proven 15%+ CTR lift.",
         49.99,523,4.9,89,["listing","template","copywriting","conversion"]),
        ("automation","TikTok Trending Products Tracker — Auto-Alert",
         "Automation workflow that monitors TikTok Shop hourly, scores viral potential, and sends alerts when products hit your criteria. No-code setup.",
         39.99,312,4.7,67,["automation","tiktok","trending","alerts"]),
        ("keyword_list","Etsy SEO Master List — Handmade & Vintage 2026",
         "800 Etsy-specific long-tail keywords with monthly search data, competition level, and seasonal trends. Perfect for shop optimization.",
         24.99,198,4.6,41,["etsy","seo","keywords","handmade"]),
        ("template","Supplier Negotiation Email Templates (12-Pack)",
         "Battle-tested email scripts for: first contact, price negotiation, MOQ reduction, sample requests, and payment term extension. Used by 7-figure sellers.",
         19.99,634,4.9,118,["supplier","negotiation","email","templates"]),
        ("automation","Inventory Reorder Alert System",
         "Monitors your inventory levels and auto-creates reorder tasks when stock hits your threshold. Integrates with Alibaba supplier emails.",
         34.99,287,4.7,54,["inventory","automation","reorder","alert"]),
        ("keyword_list","Walmart Marketplace Top Keywords 2026",
         "400 high-traffic Walmart.com keywords with buy-box competitiveness scores. Filtered for products with fewer than 20 top sellers.",
         19.99,156,4.5,33,["walmart","keywords","marketplace","seo"]),
        ("template","Amazon PPC Campaign Structure Templates",
         "Complete PPC campaign architecture for 5 budget levels ($500-$10k/mo). Includes Sponsored Products, Brands, Display setup guides and bid strategies.",
         59.99,423,4.8,97,["ppc","amazon","advertising","campaign"]),
        ("automation","Cross-Platform Price Monitor",
         "Tracks your products across Amazon, Walmart, eBay and Shopify. Alerts you when a competitor drops price by more than 5%. Auto-suggests repricing.",
         44.99,389,4.8,76,["pricing","automation","competitor","repricing"]),
        ("keyword_list","Home & Kitchen Trend Keywords — Summer 2026",
         "350 seasonally-trending keywords for the home & kitchen category with week-over-week growth rates and TikTok correlation scores.",
         22.99,211,4.6,48,["home-kitchen","seasonal","trending","summer"]),
        ("template","Complete Launch Playbook — New Product Launch SOP",
         "Step-by-step 90-day launch playbook: pre-launch checklist, launch week PPC structure, review generation strategy, BSR climbing tactics.",
         79.99,167,4.9,44,["launch","strategy","playbook","amazon"]),
        ("automation","Review Request Automation (Compliant)",
         "Automated review request sequence using Amazon's Request a Review button. Fully TOS-compliant timing logic, excludes refunded/returned orders.",
         29.99,542,4.7,103,["reviews","automation","amazon","compliance"]),
    ]
    ast_inserted = 0
    for a in assets:
        cur.execute("""
            INSERT INTO marketplace_assets
              (id, creator_id, type, name, description, price,
               downloads, rating, rating_count, tags,
               is_published, is_verified, created_at, updated_at)
            VALUES (gen_random_uuid(), %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    true, true, NOW(), NOW())
        """, (USER_ID, a[0], a[1], a[2], a[3], a[4], a[5], a[6], a[7]))
        ast_inserted += 1
    print(f"  marketplace_assets: {ast_inserted} inserted")

    # ── 6. SUPPLIERS ──────────────────────────────────────────────
    suppliers = [
        # (name, country, contact_name, contact_email, contact_phone,
        #  website, alibaba_url, trust_score, risk_score, quality_score, reliability_score,
        #  avg_lead_time_days, min_order_qty, payment_terms, shipping_methods, certifications)
        ("Shenzhen EcoMaterials Co. Ltd","CN","David Chen","david@ecomatcn.com","+86-755-8821-4400",
         "https://ecomatcn.com","https://ecomatcn.alibaba.com",
         92,18,91,89,18,500,"30% deposit, 70% before shipment",
         ["sea","air","express"],["ISO9001","FSC","BSCI"]),
        ("Yiwu FitGear Manufacturing","CN","Lisa Wang","lisa@yiwufitgear.com","+86-579-8234-5500",
         "https://yiwufitgear.com","https://yiwufitgear.alibaba.com",
         88,22,87,85,21,300,"T/T 30 days",
         ["sea","express"],["ISO9001","SGS","CE"]),
        ("Guangzhou LightTech Solutions","CN","Kevin Zhou","kevin@gzlighttech.com","+86-20-6678-9900",
         "https://gzlighttech.com","https://gzlighttech.alibaba.com",
         85,28,84,82,25,200,"T/T 50/50",
         ["sea","air"],["CE","RoHS","FCC"]),
        ("Vietnam NatureCraft Export","VN","Minh Nguyen","minh@vnaturecraft.vn","+84-28-3823-4400",
         "https://naturecraftvn.com",None,
         79,31,83,80,35,100,"50% advance",
         ["sea","air"],["OEKO-TEX","WRAP"]),
        ("India AromaSource Pvt Ltd","IN","Priya Sharma","priya@aromasource.in","+91-80-4123-5600",
         "https://aromasource.in",None,
         83,25,86,84,28,250,"L/C or T/T",
         ["sea","air"],["ISO22000","HACCP","GMP"]),
        ("Ningbo PackPro Industrial","CN","Tony Xu","tony@nbnpackpro.com","+86-574-8923-4400",
         "https://nbnpackpro.com","https://nbnpackpro.alibaba.com",
         90,19,89,91,16,1000,"D/P or T/T",
         ["sea","express"],["ISO9001","FSC","SMETA"]),
        ("Poland HandCraft Artisans","PL","Marta Kowalski","marta@plhandcraft.eu","+48-22-555-8800",
         "https://plhandcraft.eu",None,
         76,34,88,78,42,50,"PayPal or bank transfer",
         ["express","air"],["CE","REACH"]),
        ("Taiwan SilicoPure Technology","TW","James Lin","james@silicopure.tw","+886-4-2358-7700",
         "https://silicopure.tw",None,
         94,14,95,93,14,300,"T/T or L/C",
         ["sea","air","express"],["FDA","LFGB","REACH","ISO9001"]),
    ]
    sup_inserted = 0
    for s in suppliers:
        cur.execute("""
            INSERT INTO suppliers
              (id, name, country, contact_name, contact_email, contact_phone,
               website, alibaba_url,
               trust_score, risk_score, quality_score, reliability_score,
               avg_lead_time_days, min_order_qty, payment_terms,
               shipping_methods, certifications,
               created_at, updated_at)
            VALUES (gen_random_uuid(),%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                    NOW(), NOW())
        """, s)
        sup_inserted += 1
    print(f"  suppliers: {sup_inserted} inserted")

    # ── 7. TRENDS (additional rows) ───────────────────────────────
    trends = [
        # (topic, source, category, trend_score, momentum_score, viral_score,
        #  lifespan_prediction, peak_date_estimate, related_products)
        ("Eco-Friendly Kitchen Swaps","tiktok","home",91,88,79,"sustained","2026-09-01",
         ["bamboo utensils","beeswax wraps","silicone bags"]),
        ("Portable Workout Equipment","instagram","fitness",87,82,71,"seasonal","2026-08-01",
         ["resistance bands","jump rope","pull-up bar"]),
        ("Aesthetic Room Lighting","tiktok","home-decor",94,91,88,"sustained","2026-12-01",
         ["mushroom lamp","LED strips","neon signs"]),
        ("Mini Kitchen Appliances","tiktok","kitchen",89,86,83,"sustained","2026-10-01",
         ["mini waffle maker","cloud ice cream","mini donut maker"]),
        ("Wellness & Self-Care Sets","pinterest","beauty",83,79,68,"evergreen","2026-11-01",
         ["essential oil diffuser","face roller","bath salts"]),
        ("Personalized Gifts","etsy","gifts",82,76,72,"seasonal","2026-12-15",
         ["custom journal","engraved keychain","photo book"]),
        ("Summer Hydration Products","amazon","sports",86,89,74,"seasonal","2026-07-01",
         ["insulated bottle","electrolyte packets","cooling towel"]),
        ("Zero-Waste Home Products","google","eco",88,84,65,"sustained","2026-10-01",
         ["reusable bags","compost bin","bamboo products"]),
        ("Home Gym Starter Sets","youtube","fitness",85,80,69,"sustained","2026-09-01",
         ["resistance bands","yoga mat","foam roller"]),
        ("Boho Home Decor","pinterest","home-decor",80,74,71,"evergreen","2026-11-01",
         ["macrame wall hanging","rattan furniture","woven baskets"]),
    ]
    tr_inserted = 0
    for t in trends:
        cur.execute("""
            INSERT INTO trends
              (id, topic, source, category,
               trend_score, momentum_score, viral_score,
               lifespan_prediction, peak_date_estimate,
               related_products, detected_at, created_at, updated_at)
            VALUES (gen_random_uuid(),%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW(),NOW(),NOW())
        """, t)
        tr_inserted += 1
    print(f"  trends: {tr_inserted} inserted")

    conn.commit()
    print("\n✅ Seed complete — committed.")

    # ── Verify final counts ───────────────────────────────────────
    print("\n=== Final row counts ===")
    for table in ["products","inventory","keywords","listings","marketplace_assets","suppliers","trends"]:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        print(f"  {table}: {cur.fetchone()[0]}")

    conn.close()

if __name__ == "__main__":
    run()
