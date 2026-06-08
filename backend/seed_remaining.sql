-- ============================================================
-- Seed remaining tables: suppliers, supplier_products,
-- ppc_campaigns, warehouses, keyword_metrics,
-- product_metrics, inventory_events
-- ============================================================

-- Product UUIDs for reference:
--   ebb69f74 = Bamboo Cutting Board Set
--   c2fdcd92 = Silicone Cooking Utensil Set
--   529e4d0e = LED Desk Lamp
--   b8eee474 = Resistance Bands
--   da97c78c = Water Bottle 32oz
--
-- Inventory UUIDs:
--   2d269361 = Water Bottle (qty 43)
--   2d1fd8bc = LED Desk Lamp (qty 89)
--   bf6a8ab7 = Silicone Utensil (qty 187)
--   967fdcee = Bamboo Cutting Board (qty 342)
--   82d55b2d = Resistance Bands (qty 512)
--
-- Keyword UUIDs:
--   9f194ec5 = bamboo cutting board
--   7bfc18be = silicone cooking utensils
--   3a2078f1 = led desk lamp usb
--   831acf1d = resistance bands set
--   1229a6ad = stainless steel water bottle


-- ============================================================
-- WAREHOUSES (2 rows — FBA + owned 3PL)
-- ============================================================
INSERT INTO warehouses (id, name, type, address, country_code, marketplace_codes, active)
VALUES
  ('aaaa0001-0000-0000-0000-000000000001'::UUID,
   'Amazon FBA — US East', 'fba',
   '{"city": "Robbinsville", "state": "NJ", "country": "US"}'::jsonb,
   'US', ARRAY['amazon_us'], true),

  ('aaaa0002-0000-0000-0000-000000000002'::UUID,
   'Private 3PL — Los Angeles', '3pl',
   '{"city": "Los Angeles", "state": "CA", "country": "US"}'::jsonb,
   'US', ARRAY['amazon_us', 'shopify', 'walmart'], true);

-- Backfill warehouse_id into inventory rows
UPDATE inventory SET warehouse_id = 'aaaa0001-0000-0000-0000-000000000001'::UUID
WHERE warehouse_id IS NULL;


-- ============================================================
-- SUPPLIERS (4 rows)
-- ============================================================
INSERT INTO suppliers (id, name, country, contact_name, contact_email, contact_phone,
                       website, alibaba_url, trust_score, risk_score, quality_score,
                       reliability_score, avg_lead_time_days, min_order_qty,
                       payment_terms, shipping_methods, certifications, ai_analysis)
VALUES
  ('bbbb0001-0000-0000-0000-000000000001'::UUID,
   'Shenzhen EcoMaterials Co., Ltd.', 'CN',
   'Wei Zhang', 'wei.zhang@ecomatcn.com', '+86 755 8812 4400',
   'https://ecomatcn.com', 'https://ecomatcn.1688.com',
   88, 18, 91, 86, 28, 500, 'T/T 30% deposit',
   ARRAY['sea_freight', 'air_freight', 'express'],
   ARRAY['ISO9001', 'FSC', 'CE'],
   '{"strengths": ["Specializes in bamboo/eco materials", "FSC certified", "Strong QC team"], "risks": ["Sole-source risk for bamboo SKUs", "CNY holiday delays"], "negotiation_opportunities": ["MOQ reduction possible for reorders >$20k", "2% discount for 60-day payment terms"], "overall_rating": "preferred"}'::jsonb),

  ('bbbb0002-0000-0000-0000-000000000002'::UUID,
   'Guangzhou KitchenPro Manufacturing', 'CN',
   'Linda Chen', 'linda@gzkitchenpro.com', '+86 20 6612 8800',
   'https://gzkitchenpro.com', 'https://gzkitchenpro.1688.com',
   82, 24, 85, 88, 35, 300, 'T/T 50% deposit',
   ARRAY['sea_freight', 'express'],
   ARRAY['FDA', 'LFGB', 'BPA_FREE'],
   '{"strengths": ["FDA & LFGB compliant silicone", "Low defect rate <0.8%", "Accepts small reorders"], "risks": ["Longer lead time vs competitors", "Limited color customization"], "negotiation_opportunities": ["Free samples for 3+ SKUs", "Net-30 possible after 3 orders"], "overall_rating": "approved"}'::jsonb),

  ('bbbb0003-0000-0000-0000-000000000003'::UUID,
   'Yiwu FitGear Sports Equipment', 'CN',
   'James Liu', 'james.liu@fitgear.cn', '+86 579 8521 6600',
   'https://fitgear.cn', 'https://fitgear.1688.com',
   79, 31, 82, 80, 42, 1000, 'T/T 30% deposit, 70% before shipment',
   ARRAY['sea_freight', 'express'],
   ARRAY['CE', 'REACH'],
   '{"strengths": ["Competitive pricing on rubber/latex", "Large production capacity"], "risks": ["High MOQ", "QC inconsistency on multi-pack bundles"], "negotiation_opportunities": ["MOQ 500 possible with 90-day rolling PO", "Include branded carry bag at cost"], "overall_rating": "approved"}'::jsonb),

  ('bbbb0004-0000-0000-0000-000000000004'::UUID,
   'Dongguan LightTech Electronics', 'CN',
   'Amy Wu', 'amy@dtlighttech.com', '+86 769 8843 1100',
   'https://dtlighttech.com', 'https://dtlighttech.1688.com',
   85, 22, 88, 84, 30, 200, 'T/T 30% deposit',
   ARRAY['sea_freight', 'air_freight', 'express'],
   ARRAY['CE', 'FCC', 'RoHS', 'UL'],
   '{"strengths": ["UL certified LEDs", "FCC/CE compliant", "Rapid prototyping 7 days"], "risks": ["Component cost volatility (IC shortages)", "USB-C port quality varies by batch"], "negotiation_opportunities": ["Upgrade to USB-C fast charge at +$0.40/unit", "Free QC inspection for orders >1000 units"], "overall_rating": "preferred"}'::jsonb);


-- ============================================================
-- SUPPLIER_PRODUCTS (links suppliers to products with costs)
-- ============================================================
INSERT INTO supplier_products (supplier_id, product_id, supplier_sku, unit_cost, moq,
                                sample_cost, lead_time_days, is_preferred, last_quoted_at)
VALUES
  -- Bamboo Cutting Board → EcoMaterials
  ('bbbb0001-0000-0000-0000-000000000001'::UUID,
   'ebb69f74-421c-4502-bcf5-d6f656b9ba32'::UUID,
   'ECO-BCB-3PK-001', 5.80, 500, 15.00, 28, true, NOW() - INTERVAL '10 days'),

  -- Silicone Utensils → KitchenPro
  ('bbbb0002-0000-0000-0000-000000000002'::UUID,
   'c2fdcd92-d0ef-4fca-8c0c-dd1c37ecc82f'::UUID,
   'GZK-SIL-14PC-BK', 4.20, 300, 12.00, 35, true, NOW() - INTERVAL '7 days'),

  -- Resistance Bands → FitGear
  ('bbbb0003-0000-0000-0000-000000000003'::UUID,
   'b8eee474-507d-4e52-8923-38987f194437'::UUID,
   'FG-RB-5LVL-SET', 3.10, 1000, 8.00, 42, true, NOW() - INTERVAL '14 days'),

  -- LED Desk Lamp → LightTech
  ('bbbb0004-0000-0000-0000-000000000004'::UUID,
   '529e4d0e-4127-409f-82dd-0c51f3754086'::UUID,
   'DLT-LED-DESK-05', 11.00, 200, 25.00, 30, true, NOW() - INTERVAL '5 days'),

  -- Water Bottle → multiple (EcoMaterials also handles SS products)
  ('bbbb0001-0000-0000-0000-000000000001'::UUID,
   'da97c78c-1c3d-4c16-9748-ca50b0699809'::UUID,
   'ECO-WB32-SS-001', 4.20, 500, 12.00, 28, false, NOW() - INTERVAL '20 days'),

  ('bbbb0003-0000-0000-0000-000000000003'::UUID,
   'da97c78c-1c3d-4c16-9748-ca50b0699809'::UUID,
   'FG-WB32-SS-002', 3.95, 800, 10.00, 35, true, NOW() - INTERVAL '8 days');


-- ============================================================
-- PPC CAMPAIGNS (4 more — one per remaining product, varied types)
-- ============================================================
INSERT INTO ppc_campaigns (product_id, marketplace, campaign_id, name, type, status,
                           daily_budget, spend_today, impressions, clicks, orders,
                           revenue, acos, roas, tacos, ai_recommendations)
VALUES
  -- Bamboo Cutting Board — Manual Exact (complements existing Auto)
  ('ebb69f74-421c-4502-bcf5-d6f656b9ba32'::UUID,
   'amazon', 'AMZ-CAMP-1002',
   'Premium Bamboo Cutting Board Set - Manual Exact', 'manual_exact', 'enabled',
   40.00, 31.20, 8240, 198, 16, 511.84, 18.30, 5.47, 7.40,
   '{"actions": [{"type": "increase_bid", "keyword": "bamboo cutting board set", "reason": "High conversion rate 8.1%, bid headroom available"}, {"type": "add_keyword", "keyword": "eco bamboo kitchen set", "reason": "High impression share, untapped long-tail"}], "summary": "Campaign performing above average. Recommend 15% bid increase on top 3 keywords."}'::jsonb),

  -- Silicone Cooking Utensils — Auto
  ('c2fdcd92-d0ef-4fca-8c0c-dd1c37ecc82f'::UUID,
   'amazon', 'AMZ-CAMP-1003',
   'Silicone Cooking Utensil Set 14pc - Auto', 'auto', 'enabled',
   30.00, 22.80, 5120, 134, 9, 251.91, 24.60, 4.07, 10.10,
   '{"actions": [{"type": "negate_keyword", "keyword": "cheap kitchen tools", "reason": "High impressions, zero conversions in 90 days"}, {"type": "increase_budget", "amount": 10, "reason": "Budget exhausted by 2pm daily, missing evening traffic"}], "summary": "Budget limiting reach. Recommend +$10 daily budget increase."}'::jsonb),

  -- Resistance Bands — Sponsored Display
  ('b8eee474-507d-4e52-8923-38987f194437'::UUID,
   'amazon', 'AMZ-CAMP-1004',
   'Resistance Bands Set - Sponsored Display Remarketing', 'display', 'enabled',
   20.00, 11.40, 12800, 88, 5, 114.95, 32.10, 3.12, 13.80,
   '{"actions": [{"type": "lower_bid", "audience": "competitors_pdp", "reason": "ACoS 32% above 25% target on competitor detail pages"}, {"type": "increase_bid", "audience": "product_retargeting", "reason": "Past viewer retargeting converting at 12%, below target bid"}], "summary": "Retargeting performing well; competitor targeting overpaying."}'::jsonb),

  -- LED Desk Lamp — Manual Phrase
  ('529e4d0e-4127-409f-82dd-0c51f3754086'::UUID,
   'amazon', 'AMZ-CAMP-1005',
   'LED Desk Lamp USB-C - Manual Phrase', 'manual_phrase', 'enabled',
   35.00, 28.60, 6490, 176, 14, 643.86, 15.10, 6.62, 6.20,
   '{"actions": [{"type": "increase_bid", "keyword": "led desk lamp with usb charging", "reason": "Top converting keyword at 9.1%, room for position 1 bid"}, {"type": "add_keyword", "keyword": "work from home desk lamp", "reason": "Trending search term, low competition in segment"}], "summary": "Best performing campaign in portfolio. Increase budget to capture more top-of-search."}'::jsonb),

  -- Water Bottle — Auto
  ('da97c78c-1c3d-4c16-9748-ca50b0699809'::UUID,
   'amazon', 'AMZ-CAMP-1006',
   'Stainless Steel Water Bottle 32oz - Auto', 'auto', 'paused',
   25.00, 0.00, 0, 0, 0, 0.00, NULL, NULL, NULL,
   '{"actions": [{"type": "reactivate", "reason": "Product near stockout (43 units). Reactivate after replenishment to avoid wasting ad spend on OOS product"}, {"type": "prepare_campaign", "note": "Pre-load high-performing keywords from search term report before relaunching"}], "summary": "Paused due to imminent stockout. Ready to relaunch when inventory replenished."}'::jsonb);


-- ============================================================
-- KEYWORD_METRICS (30 data points per keyword, every day for 30 days)
-- ============================================================
DO $$
DECLARE
  d INTEGER;
  ts TIMESTAMPTZ;
  -- keyword IDs
  kw_bamboo UUID := '9f194ec5-3931-4049-b864-7b8910579406';
  kw_silicone UUID := '7bfc18be-e1f2-4ee0-a302-91a786763c4a';
  kw_lamp UUID := '3a2078f1-7db8-4252-a5a8-2960a525e150';
  kw_bands UUID := '831acf1d-93a7-470a-9b5b-32f51962b62e';
  kw_bottle UUID := '1229a6ad-4ee7-4e6a-a7e5-ee7bc2b813c9';
BEGIN
  FOR d IN 0..29 LOOP
    ts := NOW() - (d || ' days')::INTERVAL;

    -- bamboo cutting board (185k base, growing)
    INSERT INTO keyword_metrics (time, keyword_id, search_volume, cpc, ranking_products, top_3_asins, sponsored_count)
    VALUES (ts, kw_bamboo,
      ROUND((185000 * (1 + (29-d)*0.003))::numeric, 0)::integer,
      ROUND((1.24 + (29-d)*0.008)::numeric, 2),
      ROUND((420 - d*2)::numeric, 0)::integer,
      ARRAY['B07QX9LMBK', 'B08ABC2222', 'B09DEF3333'],
      ROUND((52 + d*0.3)::numeric, 0)::integer);

    -- silicone cooking utensils (74k base, stable)
    INSERT INTO keyword_metrics (time, keyword_id, search_volume, cpc, ranking_products, top_3_asins, sponsored_count)
    VALUES (ts, kw_silicone,
      ROUND((74000 + (29-d)*400)::numeric, 0)::integer,
      ROUND((0.98 + (29-d)*0.004)::numeric, 2),
      ROUND((280 - d)::numeric, 0)::integer,
      ARRAY['B08CXPQ4R2', 'B09RST7890', 'B08UVW1234'],
      ROUND((38 + d*0.2)::numeric, 0)::integer);

    -- led desk lamp (48k base, growing faster)
    INSERT INTO keyword_metrics (time, keyword_id, search_volume, cpc, ranking_products, top_3_asins, sponsored_count)
    VALUES (ts, kw_lamp,
      ROUND((48000 * (1 + (29-d)*0.005))::numeric, 0)::integer,
      ROUND((1.67 + (29-d)*0.012)::numeric, 2),
      ROUND((310 - d*1.5)::numeric, 0)::integer,
      ARRAY['B08MWPQ8N3', 'B07N1BRQDJ', 'B09XYZ1234'],
      ROUND((48 + d*0.4)::numeric, 0)::integer);

    -- resistance bands (320k base, very large + steady)
    INSERT INTO keyword_metrics (time, keyword_id, search_volume, cpc, ranking_products, top_3_asins, sponsored_count)
    VALUES (ts, kw_bands,
      ROUND((320000 + (29-d)*1000)::numeric, 0)::integer,
      ROUND((1.43 + (29-d)*0.005)::numeric, 2),
      ROUND((890 - d*2)::numeric, 0)::integer,
      ARRAY['B08GY5H7T1', 'B07YMHBRJ7', 'B09FIT3456'],
      ROUND((92 + d*0.5)::numeric, 0)::integer);

    -- water bottle (550k base, high competition)
    INSERT INTO keyword_metrics (time, keyword_id, search_volume, cpc, ranking_products, top_3_asins, sponsored_count)
    VALUES (ts, kw_bottle,
      ROUND((550000 + (29-d)*2000)::numeric, 0)::integer,
      ROUND((1.89 + (29-d)*0.01)::numeric, 2),
      ROUND((1240 - d*3)::numeric, 0)::integer,
      ARRAY['B08H8JHTJZ', 'B09KLM4567', 'B09WTR7890'],
      ROUND((118 + d*0.6)::numeric, 0)::integer);

  END LOOP;
END $$;


-- ============================================================
-- PRODUCT_METRICS (30 data points per product × 5 products)
-- ============================================================
DO $$
DECLARE
  d INTEGER;
  ts TIMESTAMPTZ;
  p_bamboo UUID := 'ebb69f74-421c-4502-bcf5-d6f656b9ba32';
  p_silicone UUID := 'c2fdcd92-d0ef-4fca-8c0c-dd1c37ecc82f';
  p_lamp UUID := '529e4d0e-4127-409f-82dd-0c51f3754086';
  p_bands UUID := 'b8eee474-507d-4e52-8923-38987f194437';
  p_bottle UUID := 'da97c78c-1c3d-4c16-9748-ca50b0699809';
BEGIN
  FOR d IN 0..29 LOOP
    ts := NOW() - (d || ' days')::INTERVAL;

    -- Bamboo Cutting Board — steady rank improvement
    INSERT INTO product_metrics (time, product_id, marketplace, price, bsr_rank, bsr_category,
      review_count, review_rating, estimated_sales, estimated_revenue, seller_count,
      buy_box_seller, stock_level)
    VALUES (ts, p_bamboo, 'amazon', 34.99,
      ROUND((1240 - (29-d)*12)::numeric, 0)::integer, 'Kitchen & Dining',
      ROUND((847 + (29-d)*14)::numeric, 0)::integer,
      ROUND((4.3 + (29-d)*0.003)::numeric, 1),
      ROUND((42 + (29-d)*0.8)::numeric, 0)::integer,
      ROUND(((42 + (29-d)*0.8) * 34.99)::numeric, 2),
      3, 'SellerVision Demo', 'In Stock');

    -- Silicone Utensil Set
    INSERT INTO product_metrics (time, product_id, marketplace, price, bsr_rank, bsr_category,
      review_count, review_rating, estimated_sales, estimated_revenue, seller_count,
      buy_box_seller, stock_level)
    VALUES (ts, p_silicone, 'amazon', 27.99,
      ROUND((2180 - (29-d)*8)::numeric, 0)::integer, 'Kitchen & Dining',
      ROUND((312 + (29-d)*9)::numeric, 0)::integer,
      ROUND((4.2 + (29-d)*0.002)::numeric, 1),
      ROUND((31 + (29-d)*0.5)::numeric, 0)::integer,
      ROUND(((31 + (29-d)*0.5) * 27.99)::numeric, 2),
      2, 'SellerVision Demo', 'In Stock');

    -- LED Desk Lamp — fastest growth
    INSERT INTO product_metrics (time, product_id, marketplace, price, bsr_rank, bsr_category,
      review_count, review_rating, estimated_sales, estimated_revenue, seller_count,
      buy_box_seller, stock_level)
    VALUES (ts, p_lamp, 'amazon', 45.99,
      ROUND((890 - (29-d)*18)::numeric, 0)::integer, 'Tools & Home Improvement',
      ROUND((524 + (29-d)*18)::numeric, 0)::integer,
      ROUND((4.5 + (29-d)*0.003)::numeric, 1),
      ROUND((38 + (29-d)*1.2)::numeric, 0)::integer,
      ROUND(((38 + (29-d)*1.2) * 45.99)::numeric, 2),
      2, 'SellerVision Demo', 'In Stock');

    -- Resistance Bands — high volume, competitive
    INSERT INTO product_metrics (time, product_id, marketplace, price, bsr_rank, bsr_category,
      review_count, review_rating, estimated_sales, estimated_revenue, seller_count,
      buy_box_seller, stock_level)
    VALUES (ts, p_bands, 'amazon', 22.99,
      ROUND((420 - (29-d)*5)::numeric, 0)::integer, 'Sports & Outdoors',
      ROUND((1248 + (29-d)*22)::numeric, 0)::integer,
      ROUND((4.4 + (29-d)*0.002)::numeric, 1),
      ROUND((88 + (29-d)*1.5)::numeric, 0)::integer,
      ROUND(((88 + (29-d)*1.5) * 22.99)::numeric, 2),
      4, 'SellerVision Demo', 'In Stock');

    -- Water Bottle — near stockout later in series
    INSERT INTO product_metrics (time, product_id, marketplace, price, bsr_rank, bsr_category,
      review_count, review_rating, estimated_sales, estimated_revenue, seller_count,
      buy_box_seller, stock_level)
    VALUES (ts, p_bottle, 'amazon', 19.99,
      ROUND((680 + (29-d)*4)::numeric, 0)::integer, 'Sports & Outdoors',
      ROUND((2104 + (29-d)*28)::numeric, 0)::integer,
      ROUND((4.3 + (29-d)*0.002)::numeric, 1),
      ROUND((56 + (29-d)*0.5)::numeric, 0)::integer,
      ROUND(((56 + (29-d)*0.5) * 19.99)::numeric, 2),
      3, 'SellerVision Demo',
      CASE WHEN d < 5 THEN 'Low Stock' WHEN d < 10 THEN 'Limited' ELSE 'In Stock' END);

  END LOOP;
END $$;


-- ============================================================
-- INVENTORY_EVENTS (stock movements for each item)
-- ============================================================
DO $$
DECLARE
  -- inventory IDs
  inv_bottle UUID := '2d269361-d54e-4a01-a873-a2a89cbfeae5';   -- Water Bottle qty:43
  inv_lamp UUID   := '2d1fd8bc-f5e4-46af-8412-d387c88b59ac';   -- LED Lamp qty:89
  inv_silicone UUID := 'bf6a8ab7-7561-446e-82bb-f1850fe872c3'; -- Silicone qty:187
  inv_bamboo UUID := '967fdcee-8ecf-46d2-982e-8a38d502689a';   -- Bamboo qty:342
  inv_bands UUID  := '82d55b2d-b69f-4514-93ba-9c9f86dd2ab1';   -- Bands qty:512
BEGIN
  -- Water Bottle: started at 400, selling fast, now 43
  INSERT INTO inventory_events (time, inventory_id, event_type, quantity_change, quantity_after, reference_id, notes)
  VALUES
    (NOW()-'28 days'::INTERVAL, inv_bottle, 'inbound', 400, 400, 'PO-2026-0501', 'Initial stock receipt'),
    (NOW()-'20 days'::INTERVAL, inv_bottle, 'sale', -120, 280, 'ORD-BATCH-001', 'Amazon FBA fulfillment batch'),
    (NOW()-'12 days'::INTERVAL, inv_bottle, 'sale', -90, 190, 'ORD-BATCH-002', 'Amazon FBA fulfillment batch'),
    (NOW()-'5 days'::INTERVAL, inv_bottle, 'sale', -85, 105, 'ORD-BATCH-003', 'Amazon FBA fulfillment batch'),
    (NOW()-'2 days'::INTERVAL, inv_bottle, 'sale', -62, 43, 'ORD-BATCH-004', 'URGENT: velocity increasing, near stockout');

  -- LED Lamp: started at 350, selling steadily, inbound 200
  INSERT INTO inventory_events (time, inventory_id, event_type, quantity_change, quantity_after, reference_id, notes)
  VALUES
    (NOW()-'25 days'::INTERVAL, inv_lamp, 'inbound', 350, 350, 'PO-2026-0505', 'Initial stock receipt'),
    (NOW()-'18 days'::INTERVAL, inv_lamp, 'sale', -88, 262, 'ORD-BATCH-010', 'Amazon FBA fulfillment batch'),
    (NOW()-'10 days'::INTERVAL, inv_lamp, 'sale', -96, 166, 'ORD-BATCH-011', 'Amazon FBA fulfillment batch'),
    (NOW()-'3 days'::INTERVAL, inv_lamp, 'inbound', 200, 366, 'PO-2026-0601', 'Replenishment received at FBA'),
    (NOW()-'1 day'::INTERVAL, inv_lamp, 'sale', -277, 89, 'ORD-BATCH-012', 'Amazon FBA fulfillment batch');

  -- Silicone Utensils: healthy stock
  INSERT INTO inventory_events (time, inventory_id, event_type, quantity_change, quantity_after, reference_id, notes)
  VALUES
    (NOW()-'20 days'::INTERVAL, inv_silicone, 'inbound', 400, 400, 'PO-2026-0508', 'Initial stock receipt'),
    (NOW()-'14 days'::INTERVAL, inv_silicone, 'sale', -102, 298, 'ORD-BATCH-020', 'Amazon FBA fulfillment batch'),
    (NOW()-'7 days'::INTERVAL, inv_silicone, 'sale', -111, 187, 'ORD-BATCH-021', 'Amazon FBA fulfillment batch');

  -- Bamboo Cutting Board: best seller
  INSERT INTO inventory_events (time, inventory_id, event_type, quantity_change, quantity_after, reference_id, notes)
  VALUES
    (NOW()-'30 days'::INTERVAL, inv_bamboo, 'inbound', 600, 600, 'PO-2026-0430', 'Initial stock receipt'),
    (NOW()-'22 days'::INTERVAL, inv_bamboo, 'sale', -148, 452, 'ORD-BATCH-030', 'Amazon FBA fulfillment batch'),
    (NOW()-'15 days'::INTERVAL, inv_bamboo, 'sale', -110, 342, 'ORD-BATCH-031', 'Amazon FBA fulfillment batch');

  -- Resistance Bands: large stock, good margins
  INSERT INTO inventory_events (time, inventory_id, event_type, quantity_change, quantity_after, reference_id, notes)
  VALUES
    (NOW()-'35 days'::INTERVAL, inv_bands, 'inbound', 800, 800, 'PO-2026-0415', 'Initial bulk order'),
    (NOW()-'25 days'::INTERVAL, inv_bands, 'sale', -156, 644, 'ORD-BATCH-040', 'Amazon FBA fulfillment batch'),
    (NOW()-'15 days'::INTERVAL, inv_bands, 'sale', -132, 512, 'ORD-BATCH-041', 'Amazon FBA fulfillment batch');

END $$;
