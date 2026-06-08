-- ══════════════════════════════════════════════════════════════
--  SellerVision AI — Demo Data Seed
--  Tenant: c978f4a3-ec4c-434c-b484-cb264f963624  (slug: demo)
--  Warehouse: aaaa0001-0000-0000-0000-000000000001
--  Run: psql -U sellervision -d sellervision -f seed_demo.sql
-- ══════════════════════════════════════════════════════════════

BEGIN;

-- ── 1. PRODUCTS (20 realistic cross-platform products) ────────
INSERT INTO products (id, asin, title, brand, category, subcategory, marketplace,
  current_price, buy_box_price, cost, weight_lbs,
  is_tracked, is_own_product,
  opportunity_score, risk_score, profit_score, competition_score, market_entry_score,
  tags, created_at, updated_at)
VALUES
  ('11000001-0000-0000-0000-000000000001','B08N5WRWNW','Bamboo Cutting Board Set (3-Pack)','EcoKitchen','Home & Kitchen','Cutting Boards','amazon',
    34.99,34.99,8.50,2.1, true,true, 87,24,81,42,79,
    ARRAY['eco','bamboo','kitchen','bestseller'],'2026-01-15','2026-06-07'),
  ('11000001-0000-0000-0000-000000000002','B09G3HRMVQ','Stainless Steel Meal Prep Containers (7-Pack)','PrepMaster','Home & Kitchen','Food Storage','amazon',
    28.99,27.99,6.20,1.8, true,true, 83,31,78,55,74,
    ARRAY['meal-prep','containers','bpa-free'],'2026-01-20','2026-06-07'),
  ('11000001-0000-0000-0000-000000000003','B0CKXYZABC','Resistance Band Set (11 Piece)','FitCore','Sports & Outdoors','Exercise Bands','amazon',
    24.99,24.99,4.80,0.9, true,true, 91,19,85,38,88,
    ARRAY['fitness','resistance-bands','home-gym','trending'],'2026-02-01','2026-06-07'),
  ('11000001-0000-0000-0000-000000000004','B07XYZDEF1','LED Desk Lamp with USB Charging Port','LumiWork','Office Products','Desk Lamps','amazon',
    42.99,41.99,11.00,1.4, true,true, 79,33,72,61,71,
    ARRAY['office','lamp','usb','productivity'],'2026-02-10','2026-06-07'),
  ('11000001-0000-0000-0000-000000000005','B0BXYZ1234','Silicone Reusable Bags (10-Pack)','GreenSeal','Home & Kitchen','Storage Bags','amazon',
    19.99,19.99,4.10,0.5, true,true, 88,22,82,44,84,
    ARRAY['eco','silicone','reusable','zero-waste'],'2026-02-15','2026-06-07'),
  ('11000001-0000-0000-0000-000000000006','B0CXYZ5678','Foam Roller for Deep Tissue Massage','RecoverPro','Sports & Outdoors','Recovery Equipment','amazon',
    29.99,29.99,7.50,1.2, true,false, 76,28,71,52,68,
    ARRAY['recovery','foam-roller','fitness','massage'],'2026-02-20','2026-06-07'),
  ('11000001-0000-0000-0000-000000000007','B0DXYZ9012','Portable Phone Stand Adjustable','TechDesk','Electronics','Phone Accessories','amazon',
    15.99,15.49,3.20,0.3, true,false, 72,41,68,67,65,
    ARRAY['phone','stand','desk','adjustable'],'2026-03-01','2026-06-07'),
  ('11000001-0000-0000-0000-000000000008','B0EXYZ3456','Digital Kitchen Scale (11 lb)','PrecisionPro','Home & Kitchen','Kitchen Scales','amazon',
    22.99,22.99,5.80,0.8, true,true, 80,27,75,49,77,
    ARRAY['kitchen','scale','baking','precision'],'2026-03-05','2026-06-07'),
  ('11000001-0000-0000-0000-000000000009','B0FXYZ7890','Insulated Water Bottle 32oz','HydroVault','Sports & Outdoors','Water Bottles','amazon',
    32.99,31.99,8.00,1.1, true,true, 85,26,79,48,81,
    ARRAY['hydration','insulated','stainless','eco'],'2026-03-10','2026-06-07'),
  ('11000001-0000-0000-0000-000000000010','B0GXYZ1234','Essential Oil Diffuser 500ml','AromaZen','Health & Beauty','Diffusers','amazon',
    38.99,37.99,9.50,1.6, true,true, 82,30,77,53,76,
    ARRAY['aromatherapy','diffuser','wellness','home'],'2026-03-15','2026-06-07'),
  -- Walmart products
  ('11000001-0000-0000-0000-000000000011',NULL,'Collapsible Silicone Food Storage Bowls','FlexStore','Kitchen','Food Storage','walmart',
    16.99,16.99,3.80,0.6, true,true, 78,35,73,58,70,
    ARRAY['walmart','silicone','storage','collapsible'],'2026-03-20','2026-06-07'),
  ('11000001-0000-0000-0000-000000000012',NULL,'Non-Slip Yoga Mat Extra Thick 6mm','ZenFlow','Sports','Yoga','walmart',
    27.99,27.99,6.90,2.3, true,true, 81,29,76,51,75,
    ARRAY['yoga','mat','fitness','non-slip'],'2026-03-25','2026-06-07'),
  -- Shopify products
  ('11000001-0000-0000-0000-000000000013',NULL,'Natural Beeswax Lip Balm Set (6-Pack)','PureLip','Beauty','Lip Care','shopify',
    18.99,18.99,3.50,0.2, true,true, 89,18,84,36,87,
    ARRAY['natural','beeswax','lip-balm','organic'],'2026-04-01','2026-06-07'),
  ('11000001-0000-0000-0000-000000000014',NULL,'Hand-Poured Soy Candle Set (3-Pack)','LightHaven','Home Decor','Candles','shopify',
    44.99,44.99,12.00,1.8, true,true, 86,21,80,40,83,
    ARRAY['soy-candle','handmade','home-decor','gift'],'2026-04-05','2026-06-07'),
  -- TikTok Shop products
  ('11000001-0000-0000-0000-000000000015',NULL,'Viral Mushroom Lamp Night Light','GlowTok','Home Decor','Lighting','tiktok',
    22.99,22.99,5.00,0.7, true,false, 93,15,88,31,92,
    ARRAY['viral','tiktok','mushroom-lamp','aesthetic','trending'],'2026-04-10','2026-06-07'),
  ('11000001-0000-0000-0000-000000000016',NULL,'Cloud Ice Cream Maker Mini','FrostyTok','Kitchen','Appliances','tiktok',
    34.99,34.99,8.20,1.3, true,false, 91,17,86,33,90,
    ARRAY['viral','tiktok','ice-cream','trending','summer'],'2026-04-15','2026-06-07'),
  -- Etsy products
  ('11000001-0000-0000-0000-000000000017',NULL,'Personalized Leather Journal A5','CraftedPage','Books & Stationery','Journals','etsy',
    52.00,52.00,14.00,0.9, true,true, 84,23,79,43,81,
    ARRAY['handmade','leather','personalized','gift','etsy'],'2026-04-20','2026-06-07'),
  ('11000001-0000-0000-0000-000000000018',NULL,'Macramé Wall Hanging Boho Large','BohoWeave','Home Decor','Wall Art','etsy',
    68.00,68.00,18.00,0.6, true,true, 82,25,77,45,78,
    ARRAY['macrame','boho','handmade','wall-decor','etsy'],'2026-04-25','2026-06-07'),
  -- eBay products
  ('11000001-0000-0000-0000-000000000019',NULL,'Vintage Film Camera Fully Functional','RetroLens','Electronics','Cameras','ebay',
    89.99,87.99,35.00,1.2, true,false, 74,38,69,62,66,
    ARRAY['vintage','film-camera','retro','ebay'],'2026-05-01','2026-06-07'),
  ('11000001-0000-0000-0000-000000000020',NULL,'Collectible Enamel Pin Set (10-Pack)','PinCraft','Collectibles','Pins','ebay',
    24.99,24.99,6.50,0.2, true,false, 77,32,72,54,72,
    ARRAY['enamel-pins','collectibles','art','ebay'],'2026-05-05','2026-06-07')
ON CONFLICT (id) DO NOTHING;


-- ── 2. INVENTORY (15 items with varied stock health) ──────────
INSERT INTO inventory (id, product_id, warehouse_id, marketplace, sku,
  quantity_on_hand, quantity_reserved, quantity_inbound, reorder_point, reorder_quantity,
  lead_time_days, unit_cost, stockout_date, overstock_risk,
  last_order_date, created_at, updated_at)
VALUES
  (gen_random_uuid(),'11000001-0000-0000-0000-000000000001','aaaa0001-0000-0000-0000-000000000001','amazon','ECO-BB-001', 342,28,0,  75,200,21,8.50, NULL,false,'2026-05-15','2026-05-15','2026-06-07'),
  (gen_random_uuid(),'11000001-0000-0000-0000-000000000002','aaaa0001-0000-0000-0000-000000000001','amazon','PMP-SC-002', 187,15,150,60,180,18,6.20, NULL,false,'2026-05-20','2026-05-20','2026-06-07'),
  (gen_random_uuid(),'11000001-0000-0000-0000-000000000003','aaaa0001-0000-0000-0000-000000000001','amazon','FIT-RB-003', 18, 5, 300,50,250,14,4.80,'2026-06-21',false,'2026-05-01','2026-05-01','2026-06-07'),
  (gen_random_uuid(),'11000001-0000-0000-0000-000000000004','aaaa0001-0000-0000-0000-000000000001','amazon','LMW-DL-004', 94, 8, 0,  40,120,24,11.00,NULL,false,'2026-05-25','2026-05-25','2026-06-07'),
  (gen_random_uuid(),'11000001-0000-0000-0000-000000000005','aaaa0001-0000-0000-0000-000000000001','amazon','GRN-SB-005', 8,  2, 500,80,400,16,4.10,'2026-06-14',false,'2026-04-20','2026-04-20','2026-06-07'),
  (gen_random_uuid(),'11000001-0000-0000-0000-000000000008','aaaa0001-0000-0000-0000-000000000001','amazon','PRE-KS-008', 156,12,0,  45,150,20,5.80, NULL,false,'2026-05-30','2026-05-30','2026-06-07'),
  (gen_random_uuid(),'11000001-0000-0000-0000-000000000009','aaaa0001-0000-0000-0000-000000000001','amazon','HYD-WB-009', 412,35,0,  100,300,18,8.00, NULL,true, '2026-05-10','2026-05-10','2026-06-07'),
  (gen_random_uuid(),'11000001-0000-0000-0000-000000000010','aaaa0001-0000-0000-0000-000000000001','amazon','ARO-ED-010', 67, 6, 100,30,120,22,9.50, NULL,false,'2026-05-22','2026-05-22','2026-06-07'),
  (gen_random_uuid(),'11000001-0000-0000-0000-000000000011','aaaa0001-0000-0000-0000-000000000001','walmart','WMT-SB-011', 234,18,0, 60,200,19,3.80, NULL,false,'2026-05-18','2026-05-18','2026-06-07'),
  (gen_random_uuid(),'11000001-0000-0000-0000-000000000012','aaaa0001-0000-0000-0000-000000000001','walmart','WMT-YM-012', 5,  1, 200,40,150,21,6.90,'2026-06-18',false,'2026-04-15','2026-04-15','2026-06-07'),
  (gen_random_uuid(),'11000001-0000-0000-0000-000000000013','aaaa0001-0000-0000-0000-000000000001','shopify','SHO-LB-013', 89, 7, 0,  25,100,10,3.50, NULL,false,'2026-05-28','2026-05-28','2026-06-07'),
  (gen_random_uuid(),'11000001-0000-0000-0000-000000000014','aaaa0001-0000-0000-0000-000000000001','shopify','SHO-SC-014', 45, 3, 0,  20,80, 14,12.00,NULL,false,'2026-05-20','2026-05-20','2026-06-07'),
  (gen_random_uuid(),'11000001-0000-0000-0000-000000000015','aaaa0001-0000-0000-0000-000000000001','tiktok', 'TTK-ML-015', 3,  0, 500,100,600,14,5.00,'2026-06-10',false,'2026-04-01','2026-04-01','2026-06-07'),
  (gen_random_uuid(),'11000001-0000-0000-0000-000000000016','aaaa0001-0000-0000-0000-000000000001','tiktok', 'TTK-IC-016', 72, 9, 150,50,200,14,8.20, NULL,false,'2026-05-25','2026-05-25','2026-06-07'),
  (gen_random_uuid(),'11000001-0000-0000-0000-000000000017','aaaa0001-0000-0000-0000-000000000001','shopify','ETY-LJ-017', 28, 2, 0,  10,50, 21,14.00,NULL,false,'2026-05-15','2026-05-15','2026-06-07')
ON CONFLICT DO NOTHING;


-- ── 3. KEYWORDS (20 high-value keywords across categories) ────
INSERT INTO keywords (id, keyword, marketplace, monthly_searches, search_volume_trend,
  cpc, competition_level, difficulty_score, opportunity_score, ppc_score, seo_score,
  intent, related_keywords, created_at, updated_at)
VALUES
  (gen_random_uuid(),'bamboo cutting board','amazon',  48200,  8.2, 1.24,'medium',42,87,79,84,'commercial',ARRAY['cutting board set','bamboo kitchen','wood cutting board'],'2026-01-01','2026-06-07'),
  (gen_random_uuid(),'meal prep containers','amazon',  124000,12.5, 0.98,'high',  58,83,71,76,'commercial',ARRAY['food storage containers','glass meal prep','bpa free containers'],'2026-01-01','2026-06-07'),
  (gen_random_uuid(),'resistance bands set','amazon',  218000,22.1, 0.87,'high',  61,91,68,73,'commercial',ARRAY['exercise bands','workout bands','resistance loops'],'2026-01-01','2026-06-07'),
  (gen_random_uuid(),'led desk lamp usb','amazon',    67400,  5.4, 1.56,'medium',49,79,82,78,'commercial',ARRAY['usb desk lamp','office lamp','led lamp with usb port'],'2026-01-01','2026-06-07'),
  (gen_random_uuid(),'silicone reusable bags','amazon',84300, 18.7, 0.76,'medium',38,88,74,81,'commercial',ARRAY['reusable storage bags','silicone food bags','eco bags'],'2026-01-01','2026-06-07'),
  (gen_random_uuid(),'foam roller exercise','amazon', 142000, 9.3, 1.12,'high',  55,76,73,70,'commercial',ARRAY['foam roller massage','deep tissue roller','muscle roller'],'2026-01-01','2026-06-07'),
  (gen_random_uuid(),'insulated water bottle','amazon',396000,14.2, 1.43,'high',  69,85,66,71,'commercial',ARRAY['32oz water bottle','stainless steel bottle','hydro flask'],'2026-01-01','2026-06-07'),
  (gen_random_uuid(),'essential oil diffuser','amazon',187000, 7.8, 1.31,'high',  62,82,77,74,'commercial',ARRAY['aromatherapy diffuser','oil diffuser 500ml','ultrasonic diffuser'],'2026-01-01','2026-06-07'),
  (gen_random_uuid(),'kitchen scale digital','amazon', 93000,  6.1, 0.89,'medium',44,80,80,77,'commercial',ARRAY['food scale','baking scale','digital food scale'],'2026-01-01','2026-06-07'),
  (gen_random_uuid(),'yoga mat thick','amazon',        211000,11.9, 1.07,'high',  57,81,69,72,'commercial',ARRAY['6mm yoga mat','exercise mat','non slip yoga mat'],'2026-01-01','2026-06-07'),
  (gen_random_uuid(),'mushroom lamp led','tiktok',     312000,89.4, 0.43,'low',   18,93,91,95,'commercial',ARRAY['mushroom night light','aesthetic lamp','room decor light'],'2026-01-01','2026-06-07'),
  (gen_random_uuid(),'ice cream maker mini','tiktok',  178000,67.2, 0.38,'low',   14,91,93,96,'commercial',ARRAY['mini ice cream machine','ice cream at home','cloud ice cream'],'2026-01-01','2026-06-07'),
  (gen_random_uuid(),'soy candle handmade','shopify',  56000, 24.8, 1.68,'low',   22,86,84,88,'commercial',ARRAY['hand poured candle','natural candle','soy wax candle'],'2026-01-01','2026-06-07'),
  (gen_random_uuid(),'lip balm natural organic','shopify',42000,19.3,1.22,'medium',31,89,80,85,'commercial',ARRAY['beeswax lip balm','organic lip balm','natural lip care'],'2026-01-01','2026-06-07'),
  (gen_random_uuid(),'leather journal personalized','etsy',38000,16.7,2.14,'low', 27,84,82,87,'commercial',ARRAY['custom journal','leather notebook','personalized notebook'],'2026-01-01','2026-06-07'),
  (gen_random_uuid(),'macrame wall hanging','etsy',    64000, 21.4, 1.89,'medium',33,82,79,84,'commercial',ARRAY['boho wall decor','macrame decor','wall hanging art'],'2026-01-01','2026-06-07'),
  (gen_random_uuid(),'best meal prep containers glass','amazon',28000,31.2,1.34,'low',29,92,86,89,'informational',ARRAY['glass containers with lids','meal prep glass','microwave safe containers'],'2026-01-01','2026-06-07'),
  (gen_random_uuid(),'home gym equipment set','amazon',144000,28.9,1.61,'high',  64,88,72,68,'commercial',ARRAY['home workout equipment','gym equipment bundle','exercise equipment'],'2026-01-01','2026-06-07'),
  (gen_random_uuid(),'eco friendly kitchen products','amazon',52000,34.7,0.92,'low',24,90,83,88,'commercial',ARRAY['sustainable kitchen','eco kitchen','green kitchen products'],'2026-01-01','2026-06-07'),
  (gen_random_uuid(),'portable charger fast charging','amazon',287000,6.8,1.48,'high',71,77,74,70,'commercial',ARRAY['power bank','portable battery','fast charging power bank'],'2026-01-01','2026-06-07')
ON CONFLICT DO NOTHING;


-- ── 4. LISTINGS (15 AI-generated listings) ───────────────────
INSERT INTO listings (id, product_id, marketplace, title,
  bullet_points, description, backend_keywords,
  price, status, seo_score, completeness_score, ai_generated,
  published_at, created_at, updated_at)
VALUES
  (gen_random_uuid(),'11000001-0000-0000-0000-000000000001','amazon',
   'EcoKitchen Bamboo Cutting Board Set of 3 - Organic, Eco-Friendly, Juice Groove Design',
   ARRAY['✅ SET OF 3 SIZES: Small (9x6"), Medium (12x8"), Large (15x11") for every cutting task',
         '✅ PREMIUM BAMBOO: Harder than maple, knife-friendly, naturally antimicrobial surface',
         '✅ JUICE GROOVES: Deep channels prevent messy countertops during meat and fruit prep',
         '✅ EASY CLEAN: Hand wash only, apply mineral oil monthly to extend lifespan by years',
         '✅ SUSTAINABLE: 100% organic Moso bamboo, FSC certified, plastic-free packaging'],
   'Transform your kitchen prep with the EcoKitchen Bamboo Cutting Board Set...',
   ARRAY['bamboo','cutting board','organic','kitchen','eco-friendly','wood board','chopping board'],
   34.99,'active',94,96,true,'2026-02-01','2026-02-01','2026-06-07'),
  (gen_random_uuid(),'11000001-0000-0000-0000-000000000003','amazon',
   'FitCore Resistance Band Set 11 Piece - Home Gym Workout Bands for Men & Women',
   ARRAY['💪 11-PIECE COMPLETE SET: 5 resistance levels (10-50 lbs), handles, ankle straps, door anchor & carry bag',
         '💪 NATURAL LATEX: Premium elastic latex resists snapping, maintains tension through 10,000+ uses',
         '💪 FULL BODY WORKOUT: Glutes, arms, back, legs, shoulders — 40+ exercises in one kit',
         '💪 NON-SLIP HANDLES: Padded foam grips prevent hand fatigue during long sessions',
         '💪 LIFETIME WARRANTY: We stand behind every band with a no-questions-asked replacement policy'],
   'Get a complete gym in your living room with the FitCore 11-Piece Resistance Band Set...',
   ARRAY['resistance bands','workout','home gym','exercise bands','strength training','fitness'],
   24.99,'active',97,98,true,'2026-02-15','2026-02-15','2026-06-07'),
  (gen_random_uuid(),'11000001-0000-0000-0000-000000000005','amazon',
   'GreenSeal Reusable Silicone Food Storage Bags 10-Pack - Freezer, Microwave & Dishwasher Safe',
   ARRAY['🌿 10-PACK VALUE: 4 sandwich, 3 snack, 2 gallon, 1 stand-up pouch sizes for every need',
         '🌿 FOOD GRADE SILICONE: BPA-free, PVC-free, phthalate-free — safe for all foods',
         '🌿 LEAKPROOF SEAL: Dual-lock zipper holds tight even in the freezer',
         '🌿 SAVES MONEY: Replace 1,000+ single-use plastic bags per year',
         '🌿 ECO CERTIFIED: B-Corp certified manufacturer, carbon neutral shipping'],
   'Make the switch to sustainable storage with GreenSeal Reusable Silicone Bags...',
   ARRAY['silicone bags','reusable','eco-friendly','food storage','freezer bags','sustainable'],
   19.99,'active',96,97,true,'2026-03-01','2026-03-01','2026-06-07'),
  (gen_random_uuid(),'11000001-0000-0000-0000-000000000009','amazon',
   'HydroVault 32oz Insulated Water Bottle - 24hr Cold, 12hr Hot, Leak-Proof, BPA-Free',
   ARRAY['💧 DOUBLE-WALL VACUUM INSULATION: Drinks stay cold 24 hours, hot 12 hours — proven in -20°F to 120°F',
         '💧 LEAKPROOF LID: Wide mouth with secure locking lid, no spills in your bag',
         '💧 PREMIUM 18/8 STAINLESS: Won''t rust, retain odors, or leach chemicals',
         '💧 32OZ CAPACITY: Perfect for all-day hydration at the gym, office, or trail',
         '💧 LIFETIME GUARANTEE: One-time free replacement, no receipts needed'],
   'Stay hydrated all day with the HydroVault 32oz Insulated Bottle...',
   ARRAY['water bottle','insulated','stainless steel','32oz','hydro','leak proof','BPA free'],
   32.99,'active',95,96,true,'2026-03-15','2026-03-15','2026-06-07'),
  (gen_random_uuid(),'11000001-0000-0000-0000-000000000015','tiktok',
   'Mushroom Night Light LED Color Changing — Aesthetic Room Decor Lamp for Bedroom',
   ARRAY['🍄 16 COLOR MODES: Cycle through rainbow colors or lock your favorite with remote control',
         '🍄 SOFT WARM GLOW: Eye-safe 3000K warm white for sleep-friendly ambient lighting',
         '🍄 TOUCH & REMOTE: Switch modes by touch or included remote from across the room',
         '🍄 USB POWERED: Works with any USB-A charger, phone brick, or power bank',
         '🍄 VIRAL GIFT PICK: #1 trending bedroom decor on TikTok — perfect gift for teens'],
   'Create magical bedroom vibes with the GlowTok Mushroom Night Light...',
   ARRAY['mushroom lamp','night light','LED','room decor','aesthetic','color changing','tiktok'],
   22.99,'active',98,99,true,'2026-04-10','2026-04-10','2026-06-07'),
  (gen_random_uuid(),'11000001-0000-0000-0000-000000000013','shopify',
   'Natural Beeswax Lip Balm Set — 6-Pack Organic Flavors, Moisturizing, SPF 15',
   ARRAY['🐝 6 FLAVOR VARIETY: Honey, Vanilla, Cherry, Peppermint, Coconut & Unscented',
         '🐝 100% NATURAL: Beeswax, shea butter, vitamin E — no parabens, no petroleum',
         '🐝 SPF 15 PROTECTION: Broad-spectrum UVA/UVB protection in every stick',
         '🐝 LONG-LASTING MOISTURE: Clinically tested for 8-hour hydration',
         '🐝 ECO PACKAGING: Biodegradable tubes, recyclable box, cruelty-free certified'],
   'Treat your lips to pure nature with PureLip''s Beeswax Lip Balm Set...',
   ARRAY['lip balm','beeswax','natural','organic','SPF','moisturizing','lip care'],
   18.99,'active',93,95,true,'2026-04-01','2026-04-01','2026-06-07'),
  (gen_random_uuid(),'11000001-0000-0000-0000-000000000010','amazon',
   'AromaZen Essential Oil Diffuser 500ml — Ultrasonic, 7 LED Colors, Auto Shut-Off, Quiet',
   ARRAY['🌸 LARGE 500ML TANK: Run up to 10 hours on one fill — covers rooms up to 400 sq ft',
         '🌸 WHISPER-QUIET: Ultrasonic technology, under 30dB — won''t disturb sleep or focus',
         '🌸 7 LED MOODS: Warm amber, cool white, or cycle through 7 colors',
         '🌸 AUTO SHUT-OFF: Safely powers down when water runs out — no babysitting required',
         '🌸 WORKS WITH ALL OILS: Compatible with any brand of essential oil'],
   'Elevate your space with the AromaZen 500ml Ultrasonic Oil Diffuser...',
   ARRAY['essential oil diffuser','aromatherapy','ultrasonic','500ml','humidifier','oil diffuser'],
   38.99,'active',94,96,true,'2026-03-15','2026-03-15','2026-06-07'),
  (gen_random_uuid(),'11000001-0000-0000-0000-000000000002','amazon',
   'PrepMaster Meal Prep Containers 7-Pack — Airtight, Microwave Safe, BPA-Free, Portion Control',
   ARRAY['🥗 7-PACK SET: 3 x 28oz, 2 x 20oz, 2 x 10oz — perfect for breakfast, lunch, dinner & snacks',
         '🥗 LEAK-PROOF LID: Snap-lock tabs create an airtight seal, safe to pack in any bag',
         '🥗 MICROWAVE & DISHWASHER SAFE: Eat straight from the container, clean in seconds',
         '🥗 PORTION CONTROL: Divided compartments keep proteins, carbs, veggies separate',
         '🥗 BPA-FREE TRITAN: Crystal clear, food-safe, won''t stain or absorb odors'],
   'Crush your meal prep game with PrepMaster''s 7-Pack Containers...',
   ARRAY['meal prep containers','food storage','airtight','portion control','BPA free','microwave safe'],
   28.99,'active',92,94,true,'2026-02-01','2026-02-01','2026-06-07')
ON CONFLICT DO NOTHING;


-- ── 5. MARKETPLACE ASSETS (12 published assets) ───────────────
INSERT INTO marketplace_assets (id, creator_id, type, name, description,
  price, downloads, rating, rating_count, tags,
  is_published, is_verified, created_at, updated_at)
VALUES
  (gen_random_uuid(),'c978f4a3-ec4c-434c-b484-cb264f963624',
   'keyword_list','Top 500 Amazon FBA Keywords 2026 Q2',
   'Curated list of 500 high-opportunity keywords across 12 categories. Includes search volume, CPC, competition scores and trend data. Updated quarterly.',
   29.99,847,4.8,142,ARRAY['keywords','amazon','fba','research'],true,true,'2026-01-01','2026-06-07'),

  (gen_random_uuid(),'c978f4a3-ec4c-434c-b484-cb264f963624',
   'template','AI Listing Template Pack — 20 Niche Templates',
   'High-converting listing templates for 20 popular niches. Each template includes title formula, 5 bullet points, A+ content outline. Proven 15%+ CTR lift.',
   49.99,523,4.9,89,ARRAY['listing','template','copywriting','conversion'],true,true,'2026-01-15','2026-06-07'),

  (gen_random_uuid(),'c978f4a3-ec4c-434c-b484-cb264f963624',
   'automation','TikTok Trending Products Tracker — Auto-Alert',
   'Automation workflow that monitors TikTok Shop hourly, scores viral potential, and sends alerts when products hit your criteria. No-code setup.',
   39.99,312,4.7,67,ARRAY['automation','tiktok','trending','alerts'],true,true,'2026-02-01','2026-06-07'),

  (gen_random_uuid(),'c978f4a3-ec4c-434c-b484-cb264f963624',
   'keyword_list','Etsy SEO Master List — Handmade & Vintage 2026',
   '800 Etsy-specific long-tail keywords with monthly search data, competition level, and seasonal trends. Perfect for shop optimization.',
   24.99,198,4.6,41,ARRAY['etsy','seo','keywords','handmade'],true,true,'2026-02-15','2026-06-07'),

  (gen_random_uuid(),'c978f4a3-ec4c-434c-b484-cb264f963624',
   'template','Supplier Negotiation Email Templates (12-Pack)',
   'Battle-tested email scripts for: first contact, price negotiation, MOQ reduction, sample requests, and payment term extension. Used by 7-figure sellers.',
   19.99,634,4.9,118,ARRAY['supplier','negotiation','email','templates'],true,true,'2026-03-01','2026-06-07'),

  (gen_random_uuid(),'c978f4a3-ec4c-434c-b484-cb264f963624',
   'automation','Inventory Reorder Alert System',
   'Monitors your inventory levels and auto-creates reorder tasks when stock hits your threshold. Integrates with Alibaba supplier emails.',
   34.99,287,4.7,54,ARRAY['inventory','automation','reorder','alert'],true,true,'2026-03-10','2026-06-07'),

  (gen_random_uuid(),'c978f4a3-ec4c-434c-b484-cb264f963624',
   'keyword_list','Walmart Marketplace Top Keywords 2026',
   '400 high-traffic Walmart.com keywords with buy-box competitiveness scores. Filtered for products with <20 top sellers.',
   19.99,156,4.5,33,ARRAY['walmart','keywords','marketplace','seo'],true,true,'2026-03-20','2026-06-07'),

  (gen_random_uuid(),'c978f4a3-ec4c-434c-b484-cb264f963624',
   'template','Amazon PPC Campaign Structure Templates',
   'Complete PPC campaign architecture for 5 budget levels ($500–$10k/mo). Includes Sponsored Products, Brands, Display setup guides and bid strategies.',
   59.99,423,4.8,97,ARRAY['ppc','amazon','advertising','campaign'],true,true,'2026-04-01','2026-06-07'),

  (gen_random_uuid(),'c978f4a3-ec4c-434c-b484-cb264f963624',
   'automation','Cross-Platform Price Monitor',
   'Tracks your products across Amazon, Walmart, eBay and Shopify. Alerts you when competitor drops price by more than 5%. Auto-suggests repricing.',
   44.99,389,4.8,76,ARRAY['pricing','automation','competitor','repricing'],true,true,'2026-04-10','2026-06-07'),

  (gen_random_uuid(),'c978f4a3-ec4c-434c-b484-cb264f963624',
   'keyword_list','Home & Kitchen Trend Keywords — Summer 2026',
   '350 seasonally-trending keywords for the home & kitchen category with week-over-week growth rates and TikTok correlation scores.',
   22.99,211,4.6,48,ARRAY['home-kitchen','seasonal','trending','summer'],true,true,'2026-04-20','2026-06-07'),

  (gen_random_uuid(),'c978f4a3-ec4c-434c-b484-cb264f963624',
   'template','Complete Launch Playbook — New Product Launch SOP',
   'Step-by-step 90-day launch playbook: pre-launch checklist, launch week PPC structure, review generation strategy, BSR climbing tactics.',
   79.99,167,4.9,44,ARRAY['launch','strategy','playbook','amazon'],true,true,'2026-05-01','2026-06-07'),

  (gen_random_uuid(),'c978f4a3-ec4c-434c-b484-cb264f963624',
   'automation','Review Request Automation (Compliant)',
   'Automated review request sequence using Amazon''s Request a Review button. Fully TOS-compliant timing logic, excludes refunded/returned orders.',
   29.99,542,4.7,103,ARRAY['reviews','automation','amazon','compliance'],true,true,'2026-05-10','2026-06-07')
ON CONFLICT DO NOTHING;


-- ── 6. SUPPLIERS (8 realistic suppliers) ─────────────────────
INSERT INTO suppliers (id, name, country, contact_name, contact_email, contact_phone,
  website, alibaba_url, trust_score, risk_score, quality_score, reliability_score,
  avg_lead_time_days, min_order_qty, payment_terms,
  shipping_methods, certifications, created_at, updated_at)
VALUES
  (gen_random_uuid(),'Shenzhen EcoMaterials Co. Ltd','CN','David Chen','david@ecomatcn.com','+86-755-8821-4400',
   'https://ecomatcn.com','https://ecomatcn.alibaba.com',
   92,18,91,89, 18,500,'30% deposit, 70% before shipment',
   ARRAY['sea','air','express'],ARRAY['ISO9001','FSC','BSCI'],'2026-01-01','2026-06-07'),

  (gen_random_uuid(),'Yiwu FitGear Manufacturing','CN','Lisa Wang','lisa@yiwufitgear.com','+86-579-8234-5500',
   'https://yiwufitgear.com','https://yiwufitgear.alibaba.com',
   88,22,87,85, 21,300,'T/T 30 days',
   ARRAY['sea','express'],ARRAY['ISO9001','SGS','CE'],'2026-01-15','2026-06-07'),

  (gen_random_uuid(),'Guangzhou LightTech Solutions','CN','Kevin Zhou','kevin@gzlighttech.com','+86-20-6678-9900',
   'https://gzlighttech.com','https://gzlighttech.alibaba.com',
   85,28,84,82, 25,200,'T/T 50/50',
   ARRAY['sea','air'],ARRAY['CE','RoHS','FCC'],'2026-01-20','2026-06-07'),

  (gen_random_uuid(),'Vietnam NatureCraft Export','VN','Minh Nguyen','minh@vnaturecraft.vn','+84-28-3823-4400',
   'https://naturecraftvn.com',NULL,
   79,31,83,80, 35,100,'50% advance',
   ARRAY['sea','air'],ARRAY['OEKO-TEX','WRAP'],'2026-02-01','2026-06-07'),

  (gen_random_uuid(),'India AromaSource Pvt Ltd','IN','Priya Sharma','priya@aromasource.in','+91-80-4123-5600',
   'https://aromasource.in',NULL,
   83,25,86,84, 28,250,'L/C or T/T',
   ARRAY['sea','air'],ARRAY['ISO22000','HACCP','GMP'],'2026-02-10','2026-06-07'),

  (gen_random_uuid(),'Ningbo PackPro Industrial','CN','Tony Xu','tony@nbnpackpro.com','+86-574-8923-4400',
   'https://nbnpackpro.com','https://nbnpackpro.alibaba.com',
   90,19,89,91, 16,1000,'D/P or T/T',
   ARRAY['sea','express'],ARRAY['ISO9001','FSC','SMETA'],'2026-02-20','2026-06-07'),

  (gen_random_uuid(),'Poland HandCraft Artisans','PL','Marta Kowalski','marta@plhandcraft.eu','+48-22-555-8800',
   'https://plhandcraft.eu',NULL,
   76,34,88,78, 42,50,'PayPal or bank transfer',
   ARRAY['express','air'],ARRAY['CE','REACH'],'2026-03-01','2026-06-07'),

  (gen_random_uuid(),'Taiwan SilicoPure Technology','TW','James Lin','james@silicopure.tw','+886-4-2358-7700',
   'https://silicopure.tw',NULL,
   94,14,95,93, 14,300,'T/T or L/C',
   ARRAY['sea','air','express'],ARRAY['FDA','LFGB','REACH','ISO9001'],'2026-03-10','2026-06-07')
ON CONFLICT DO NOTHING;


-- ── 7. TRENDS (additional trending topics) ────────────────────
INSERT INTO trends (id, topic, category, source, trend_score, momentum_score, viral_score,
  search_volume, lifespan_prediction, peak_date_estimate,
  related_products, commercial_opportunity, entry_window,
  created_at, updated_at)
SELECT
  gen_random_uuid(), topic, category, source,
  trend_score, momentum_score, viral_score, search_volume,
  lifespan_prediction, peak_date_estimate::date,
  related_products, commercial_opportunity, entry_window,
  created_at::timestamptz, updated_at::timestamptz
FROM (VALUES
  ('Eco-Friendly Kitchen Swaps','home','tiktok',       91,88,79,284000,'sustained','2026-09-01',ARRAY['bamboo utensils','beeswax wraps','silicone bags'],'high','now','2026-05-01','2026-06-07'),
  ('Portable Workout Equipment','fitness','instagram',  87,82,71,198000,'seasonal', '2026-08-01',ARRAY['resistance bands','jump rope','pull-up bar'],'high','now','2026-05-05','2026-06-07'),
  ('Aesthetic Room Lighting','home-decor','tiktok',     94,91,88,376000,'sustained','2026-12-01',ARRAY['mushroom lamp','LED strips','neon signs'],'very high','now','2026-05-10','2026-06-07'),
  ('Mini Kitchen Appliances','kitchen','tiktok',        89,86,83,241000,'sustained','2026-10-01',ARRAY['mini waffle maker','cloud ice cream','mini donut maker'],'high','now','2026-05-12','2026-06-07'),
  ('Wellness & Self-Care Sets','beauty','pinterest',    83,79,68,167000,'evergreen', '2026-11-01',ARRAY['essential oil diffuser','face roller','bath salts'],'high','now','2026-05-15','2026-06-07'),
  ('Personalized Gifts','gifts','etsy',                 82,76,72,312000,'seasonal','2026-12-15',ARRAY['custom journal','engraved keychain','photo book'],'high','holiday','2026-05-18','2026-06-07'),
  ('Summer Hydration Products','sports','amazon',       86,89,74,203000,'seasonal','2026-07-01',ARRAY['insulated bottle','electrolyte packets','cooling towel'],'high','now','2026-05-20','2026-06-07'),
  ('Zero-Waste Home Products','eco','google',           88,84,65,142000,'sustained','2026-10-01',ARRAY['reusable bags','compost bin','bamboo products'],'high','now','2026-05-22','2026-06-07'),
  ('Home Gym Starter Sets','fitness','youtube',         85,80,69,178000,'sustained','2026-09-01',ARRAY['resistance bands','yoga mat','foam roller'],'high','now','2026-05-25','2026-06-07'),
  ('Boho Home Decor','home-decor','pinterest',          80,74,71,134000,'evergreen','2026-11-01',ARRAY['macrame wall hanging','rattan furniture','woven baskets'],'medium','now','2026-05-28','2026-06-07')
) AS t(topic,category,source,trend_score,momentum_score,viral_score,search_volume,
       lifespan_prediction,peak_date_estimate,related_products,commercial_opportunity,
       entry_window,created_at,updated_at)
ON CONFLICT DO NOTHING;

COMMIT;

-- ── Verification ─────────────────────────────────────────────
SELECT tablename, COUNT(*) as rows
FROM pg_tables
JOIN LATERAL (SELECT COUNT(*) FROM information_schema.tables) x ON true
WHERE schemaname = 'public'
  AND tablename IN ('products','inventory','keywords','listings','marketplace_assets','suppliers','trends')
GROUP BY tablename
ORDER BY tablename;
