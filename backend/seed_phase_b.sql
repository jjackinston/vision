-- Phase B: notifications, workflows, agent_runs, marketplace_connections
-- user_id:   8e63fa3b-4d49-4943-aeb7-ebf1b41e4825
-- tenant_id: c978f4a3-ec4c-434c-b484-cb264f963624

-- ============================================================
-- MARKETPLACE_CONNECTIONS (4 rows — Amazon connected, others pending)
-- ============================================================
INSERT INTO marketplace_connections
  (id, tenant_id, marketplace, account_name, credentials, status, last_sync_at, sync_config)
VALUES
  ('cc000001-0000-0000-0000-000000000001'::UUID,
   'c978f4a3-ec4c-434c-b484-cb264f963624'::UUID,
   'amazon', 'SellerVision Demo Store',
   '{"seller_id": "A1DEMO12345", "region": "NA", "mode": "sandbox"}'::jsonb,
   'connected', NOW() - INTERVAL '2 hours',
   '{"sync_products": true, "sync_orders": true, "sync_inventory": true, "sync_ppc": true, "auto_sync_interval_minutes": 60}'::jsonb),

  ('cc000002-0000-0000-0000-000000000002'::UUID,
   'c978f4a3-ec4c-434c-b484-cb264f963624'::UUID,
   'walmart', 'SellerVision Walmart Account',
   '{"client_id": "demo-client", "mode": "sandbox"}'::jsonb,
   'pending', NULL,
   '{"sync_products": true, "sync_orders": false, "sync_inventory": true}'::jsonb),

  ('cc000003-0000-0000-0000-000000000003'::UUID,
   'c978f4a3-ec4c-434c-b484-cb264f963624'::UUID,
   'shopify', 'SellerVision Shopify Store',
   '{"shop_domain": "sellervision-demo.myshopify.com", "mode": "sandbox"}'::jsonb,
   'pending', NULL,
   '{"sync_products": true, "sync_orders": true, "sync_inventory": false}'::jsonb),

  ('cc000004-0000-0000-0000-000000000004'::UUID,
   'c978f4a3-ec4c-434c-b484-cb264f963624'::UUID,
   'tiktok_shop', 'SellerVision TikTok Shop',
   '{"access_token": "demo-token", "region": "US", "mode": "sandbox"}'::jsonb,
   'error', NOW() - INTERVAL '5 hours',
   '{"sync_products": true, "sync_orders": true}'::jsonb);


-- ============================================================
-- WORKFLOWS (5 rows — realistic automation rules)
-- ============================================================
INSERT INTO workflows
  (id, name, description, trigger_type, trigger_config, steps, is_active, last_run_at, run_count)
VALUES
  ('wf000001-0000-0000-0000-000000000001'::UUID,
   'Low Stock Alert & Reorder', 'Auto-detect products below reorder point and create PO draft',
   'schedule',
   '{"cron": "0 9 * * *", "timezone": "America/New_York"}'::jsonb,
   '[
     {"step": 1, "action": "check_inventory", "config": {"threshold": "reorder_point"}},
     {"step": 2, "action": "create_po_draft", "config": {"auto_submit": false}},
     {"step": 3, "action": "notify", "config": {"channels": ["email", "in_app"], "template": "low_stock_alert"}}
   ]'::jsonb,
   true, NOW() - INTERVAL '6 hours', 47),

  ('wf000002-0000-0000-0000-000000000002'::UUID,
   'Daily PPC Budget Optimizer', 'Adjust campaign budgets based on ROAS performance each morning',
   'schedule',
   '{"cron": "0 7 * * 1-5", "timezone": "America/New_York"}'::jsonb,
   '[
     {"step": 1, "action": "fetch_ppc_metrics", "config": {"lookback_days": 7}},
     {"step": 2, "action": "compute_optimal_bids", "config": {"target_acos": 20, "max_bid_change_pct": 15}},
     {"step": 3, "action": "apply_bid_changes", "config": {"dry_run": false, "min_spend_threshold": 5}},
     {"step": 4, "action": "notify", "config": {"channels": ["in_app"]}}
   ]'::jsonb,
   true, NOW() - INTERVAL '1 hour', 124),

  ('wf000003-0000-0000-0000-000000000003'::UUID,
   'Competitor Price Watch', 'Monitor competitor prices and alert when undercutting by >10%',
   'event',
   '{"event": "competitor_price_change", "threshold_pct": 10}'::jsonb,
   '[
     {"step": 1, "action": "fetch_competitor_prices", "config": {"marketplaces": ["amazon"]}},
     {"step": 2, "action": "compare_prices", "config": {"alert_threshold_pct": 10}},
     {"step": 3, "action": "notify", "config": {"channels": ["email", "in_app"], "priority": "high"}}
   ]'::jsonb,
   true, NOW() - INTERVAL '3 hours', 89),

  ('wf000004-0000-0000-0000-000000000004'::UUID,
   'Weekly AI Listing Audit', 'Run SEO audit on all listings every Sunday and queue optimizations',
   'schedule',
   '{"cron": "0 10 * * 0", "timezone": "America/New_York"}'::jsonb,
   '[
     {"step": 1, "action": "list_active_listings", "config": {}},
     {"step": 2, "action": "run_seo_audit", "config": {"min_score_threshold": 80}},
     {"step": 3, "action": "queue_optimizations", "config": {"auto_apply": false}},
     {"step": 4, "action": "notify", "config": {"channels": ["email"], "include_report": true}}
   ]'::jsonb,
   true, NOW() - INTERVAL '6 days', 12),

  ('wf000005-0000-0000-0000-000000000005'::UUID,
   'Trend-to-Product Pipeline', 'When a viral trend detected (score >85), auto-research sourcing options',
   'event',
   '{"event": "trend_detected", "min_viral_score": 85}'::jsonb,
   '[
     {"step": 1, "action": "analyze_trend", "config": {"depth": "full"}},
     {"step": 2, "action": "search_suppliers", "config": {"countries": ["CN", "VN"], "max_results": 5}},
     {"step": 3, "action": "estimate_margins", "config": {"target_roi": 40}},
     {"step": 4, "action": "create_opportunity_report", "config": {}},
     {"step": 5, "action": "notify", "config": {"channels": ["email", "in_app"], "priority": "high"}}
   ]'::jsonb,
   false, NOW() - INTERVAL '2 days', 3);


-- ============================================================
-- AGENT_RUNS (14 rows — recent runs for all 7 agents)
-- ============================================================
INSERT INTO agent_runs
  (id, agent_type, status, input, output, steps, tokens_used, cost_usd, started_at, completed_at)
VALUES
  -- Product Research (2 runs)
  ('ar000001-0000-0000-0000-000000000001'::UUID,
   'product_research', 'completed',
   '{"marketplace": "amazon", "category": "kitchen", "min_opportunity_score": 70}'::jsonb,
   '{"products_found": 47, "high_opportunity": 8, "top_pick": "Bamboo Cutting Board Set", "opportunity_score": 91}'::jsonb,
   '[{"step": "scrape_categories", "duration_ms": 3200}, {"step": "score_products", "duration_ms": 1800}, {"step": "filter_results", "duration_ms": 400}]'::jsonb,
   4820, 0.0145, NOW() - INTERVAL '2 hours', NOW() - INTERVAL '2 hours' + INTERVAL '56 seconds'),

  ('ar000002-0000-0000-0000-000000000002'::UUID,
   'product_research', 'completed',
   '{"marketplace": "amazon", "category": "fitness", "min_opportunity_score": 75}'::jsonb,
   '{"products_found": 31, "high_opportunity": 5, "top_pick": "Resistance Bands Set", "opportunity_score": 88}'::jsonb,
   '[{"step": "scrape_categories", "duration_ms": 2900}, {"step": "score_products", "duration_ms": 1600}, {"step": "filter_results", "duration_ms": 350}]'::jsonb,
   3940, 0.0118, NOW() - INTERVAL '4 hours', NOW() - INTERVAL '4 hours' + INTERVAL '49 seconds'),

  -- Trend Agent (2 runs)
  ('ar000003-0000-0000-0000-000000000003'::UUID,
   'trend', 'completed',
   '{"sources": ["tiktok", "google"], "categories": ["kitchen", "fitness"]}'::jsonb,
   '{"trends_detected": 8, "viral_score_avg": 78, "top_trend": "Stanley Cup Dupe Water Bottles", "viral_score": 96}'::jsonb,
   '[{"step": "scan_tiktok", "duration_ms": 4100}, {"step": "scan_google_trends", "duration_ms": 2800}, {"step": "correlate", "duration_ms": 900}]'::jsonb,
   6210, 0.0186, NOW() - INTERVAL '1 hour', NOW() - INTERVAL '1 hour' + INTERVAL '1 minute 12 seconds'),

  ('ar000004-0000-0000-0000-000000000004'::UUID,
   'trend', 'completed',
   '{"sources": ["reddit", "pinterest"], "categories": ["home", "eco"]}'::jsonb,
   '{"trends_detected": 4, "viral_score_avg": 68, "top_trend": "Eco-Friendly Kitchen Accessories", "viral_score": 75}'::jsonb,
   '[{"step": "scan_reddit", "duration_ms": 3600}, {"step": "scan_pinterest", "duration_ms": 3100}, {"step": "correlate", "duration_ms": 800}]'::jsonb,
   5480, 0.0164, NOW() - INTERVAL '5 hours', NOW() - INTERVAL '5 hours' + INTERVAL '1 minute 7 seconds'),

  -- Competitor Agent (2 runs)
  ('ar000005-0000-0000-0000-000000000005'::UUID,
   'competitor', 'completed',
   '{"product_id": "ebb69f74-421c-4502-bcf5-d6f656b9ba32", "depth": "full"}'::jsonb,
   '{"competitors_analyzed": 3, "weaknesses_found": 6, "top_opportunity": "Durability complaints in 18% of reviews", "threat_level": "high"}'::jsonb,
   '[{"step": "fetch_asins", "duration_ms": 1200}, {"step": "mine_reviews", "duration_ms": 8400}, {"step": "identify_weaknesses", "duration_ms": 2100}]'::jsonb,
   9830, 0.0295, NOW() - INTERVAL '3 hours', NOW() - INTERVAL '3 hours' + INTERVAL '1 minute 58 seconds'),

  ('ar000006-0000-0000-0000-000000000006'::UUID,
   'competitor', 'completed',
   '{"product_id": "da97c78c-1c3d-4c16-9748-ca50b0699809", "depth": "full"}'::jsonb,
   '{"competitors_analyzed": 2, "weaknesses_found": 4, "top_opportunity": "Lid leakage in 24% of reviews", "threat_level": "high"}'::jsonb,
   '[{"step": "fetch_asins", "duration_ms": 1100}, {"step": "mine_reviews", "duration_ms": 7900}, {"step": "identify_weaknesses", "duration_ms": 1900}]'::jsonb,
   8640, 0.0259, NOW() - INTERVAL '8 hours', NOW() - INTERVAL '8 hours' + INTERVAL '1 minute 44 seconds'),

  -- Inventory Agent (2 runs)
  ('ar000007-0000-0000-0000-000000000007'::UUID,
   'inventory', 'completed',
   '{"check_stockout": true, "check_overstock": true}'::jsonb,
   '{"stockouts_predicted": 2, "overstock_items": 0, "action_required": ["Water Bottle (7 days)", "LED Desk Lamp (10 days)"], "reorder_value": 8240}'::jsonb,
   '[{"step": "fetch_inventory", "duration_ms": 800}, {"step": "calc_velocity", "duration_ms": 1200}, {"step": "predict_stockout", "duration_ms": 600}]'::jsonb,
   2180, 0.0065, NOW() - INTERVAL '30 minutes', NOW() - INTERVAL '30 minutes' + INTERVAL '28 seconds'),

  ('ar000008-0000-0000-0000-000000000008'::UUID,
   'inventory', 'completed',
   '{"check_stockout": true, "check_overstock": true}'::jsonb,
   '{"stockouts_predicted": 2, "overstock_items": 0, "action_required": ["Water Bottle", "LED Lamp"], "reorder_value": 8100}'::jsonb,
   '[{"step": "fetch_inventory", "duration_ms": 750}, {"step": "calc_velocity", "duration_ms": 1100}, {"step": "predict_stockout", "duration_ms": 580}]'::jsonb,
   2050, 0.0062, NOW() - INTERVAL '6 hours', NOW() - INTERVAL '6 hours' + INTERVAL '25 seconds'),

  -- PPC Agent (2 runs)
  ('ar000009-0000-0000-0000-000000000009'::UUID,
   'ppc', 'completed',
   '{"optimization_goal": "acos", "target_acos": 20, "campaigns": "all"}'::jsonb,
   '{"campaigns_analyzed": 6, "bids_adjusted": 4, "keywords_paused": 2, "keywords_added": 3, "projected_savings": 142, "projected_revenue_lift": 890}'::jsonb,
   '[{"step": "fetch_campaigns", "duration_ms": 1400}, {"step": "analyze_performance", "duration_ms": 2200}, {"step": "compute_bids", "duration_ms": 1800}, {"step": "apply_changes", "duration_ms": 600}]'::jsonb,
   7340, 0.0220, NOW() - INTERVAL '1 hour', NOW() - INTERVAL '1 hour' + INTERVAL '2 minutes 5 seconds'),

  ('ar000010-0000-0000-0000-000000000010'::UUID,
   'ppc', 'completed',
   '{"optimization_goal": "roas", "target_roas": 5, "campaigns": "all"}'::jsonb,
   '{"campaigns_analyzed": 6, "bids_adjusted": 3, "keywords_paused": 1, "keywords_added": 2, "projected_savings": 98, "projected_revenue_lift": 620}'::jsonb,
   '[{"step": "fetch_campaigns", "duration_ms": 1350}, {"step": "analyze_performance", "duration_ms": 2100}, {"step": "compute_bids", "duration_ms": 1700}, {"step": "apply_changes", "duration_ms": 580}]'::jsonb,
   6980, 0.0209, NOW() - INTERVAL '7 hours', NOW() - INTERVAL '7 hours' + INTERVAL '1 minute 58 seconds'),

  -- Supplier Agent (1 run)
  ('ar000011-0000-0000-0000-000000000011'::UUID,
   'supplier', 'completed',
   '{"action": "risk_assessment", "supplier_ids": ["bbbb0001-0000-0000-0000-000000000001", "bbbb0003-0000-0000-0000-000000000003"]}'::jsonb,
   '{"suppliers_analyzed": 2, "risk_flags": 1, "flag": "FitGear MOQ too high for Q4 demand spike", "negotiation_opportunities": 2, "estimated_cost_savings": 1840}'::jsonb,
   '[{"step": "fetch_suppliers", "duration_ms": 900}, {"step": "assess_risks", "duration_ms": 3200}, {"step": "identify_opportunities", "duration_ms": 1400}]'::jsonb,
   8120, 0.0244, NOW() - INTERVAL '12 hours', NOW() - INTERVAL '12 hours' + INTERVAL '1 minute 38 seconds'),

  -- Listing Agent (2 runs)
  ('ar000012-0000-0000-0000-000000000012'::UUID,
   'listing', 'completed',
   '{"action": "seo_audit", "marketplace": "amazon", "listings": "all"}'::jsonb,
   '{"listings_audited": 5, "avg_seo_score": 91.1, "issues_found": 3, "auto_optimizations_queued": 2, "estimated_traffic_lift": "14%"}'::jsonb,
   '[{"step": "fetch_listings", "duration_ms": 600}, {"step": "audit_seo", "duration_ms": 4800}, {"step": "queue_optimizations", "duration_ms": 400}]'::jsonb,
   11240, 0.0337, NOW() - INTERVAL '4 hours', NOW() - INTERVAL '4 hours' + INTERVAL '1 minute 34 seconds'),

  ('ar000013-0000-0000-0000-000000000013'::UUID,
   'listing', 'completed',
   '{"action": "keyword_refresh", "marketplace": "amazon"}'::jsonb,
   '{"keywords_refreshed": 5, "new_keywords_discovered": 8, "avg_search_volume": 235400, "top_opportunity": "bamboo kitchen organizer set"}'::jsonb,
   '[{"step": "fetch_keywords", "duration_ms": 700}, {"step": "research_new", "duration_ms": 5200}, {"step": "update_listings", "duration_ms": 900}]'::jsonb,
   9870, 0.0296, NOW() - INTERVAL '9 hours', NOW() - INTERVAL '9 hours' + INTERVAL '1 minute 22 seconds'),

  -- One running right now (product_research)
  ('ar000014-0000-0000-0000-000000000014'::UUID,
   'product_research', 'running',
   '{"marketplace": "amazon", "category": "home_office", "min_opportunity_score": 70}'::jsonb,
   NULL, NULL, 0, 0.0000,
   NOW() - INTERVAL '45 seconds', NULL);


-- ============================================================
-- NOTIFICATIONS (12 rows — mix of read/unread, all types)
-- ============================================================
INSERT INTO notifications
  (id, user_id, type, title, body, action_url, metadata, is_read, created_at)
VALUES
  -- URGENT unread alerts
  ('nn000001-0000-0000-0000-000000000001'::UUID,
   '8e63fa3b-4d49-4943-aeb7-ebf1b41e4825'::UUID,
   'stockout_alert', '⚠️ Stockout Alert: Water Bottle 32oz',
   'At current velocity, Water Bottle 32oz will be out of stock in 7 days (June 12). Inbound: 0 units. Reorder immediately.',
   '/inventory', '{"product_id": "da97c78c", "days_to_stockout": 7, "qty_on_hand": 43, "daily_velocity": 6.1}'::jsonb,
   false, NOW() - INTERVAL '30 minutes'),

  ('nn000002-0000-0000-0000-000000000002'::UUID,
   '8e63fa3b-4d49-4943-aeb7-ebf1b41e4825'::UUID,
   'stockout_alert', '⚠️ Stockout Alert: LED Desk Lamp',
   'LED Desk Lamp predicted to stock out in 10 days (June 15). Current stock: 89 units at 8.9/day velocity.',
   '/inventory', '{"product_id": "529e4d0e", "days_to_stockout": 10, "qty_on_hand": 89, "daily_velocity": 8.9}'::jsonb,
   false, NOW() - INTERVAL '31 minutes'),

  ('nn000003-0000-0000-0000-000000000003'::UUID,
   '8e63fa3b-4d49-4943-aeb7-ebf1b41e4825'::UUID,
   'trend_alert', '🔥 Viral Trend: Stanley Cup Dupe (Score: 96)',
   'TikTok views surging on 32oz insulated tumblers. 340% growth rate. Your Water Bottle is positioned to capitalize.',
   '/trends', '{"trend_topic": "Stanley Cup Dupe", "viral_score": 96, "growth_rate": 340}'::jsonb,
   false, NOW() - INTERVAL '1 hour'),

  ('nn000004-0000-0000-0000-000000000004'::UUID,
   '8e63fa3b-4d49-4943-aeb7-ebf1b41e4825'::UUID,
   'ppc_alert', '📉 PPC: ACoS Spike on Silicone Utensil Auto',
   'Silicone Cooking Utensil Auto campaign ACoS hit 24.6% (target: 20%). Budget exhausted by 2pm daily — missing evening traffic.',
   '/ppc', '{"campaign_id": "AMZ-CAMP-1003", "acos": 24.6, "target_acos": 20, "action": "increase_budget"}'::jsonb,
   false, NOW() - INTERVAL '2 hours'),

  ('nn000005-0000-0000-0000-000000000005'::UUID,
   '8e63fa3b-4d49-4943-aeb7-ebf1b41e4825'::UUID,
   'competitor_alert', '🎯 Competitor Price Drop: BambooKing → $28.99',
   'BambooKing dropped price from $32.99 to $28.99 (-12%). Your Bamboo Cutting Board at $34.99 is now 21% higher.',
   '/competitors', '{"brand": "BambooKing", "old_price": 32.99, "new_price": 28.99, "your_price": 34.99}'::jsonb,
   false, NOW() - INTERVAL '3 hours'),

  -- Positive alerts (unread)
  ('nn000006-0000-0000-0000-000000000006'::UUID,
   '8e63fa3b-4d49-4943-aeb7-ebf1b41e4825'::UUID,
   'milestone', '🎉 Revenue Milestone: $68K This Month!',
   'You hit $68,717 in revenue this period — +22% vs last month. Profit up +24%. Best month on record.',
   '/analytics', '{"revenue": 68717, "revenue_change": 22, "profit_change": 24}'::jsonb,
   false, NOW() - INTERVAL '4 hours'),

  ('nn000007-0000-0000-0000-000000000007'::UUID,
   '8e63fa3b-4d49-4943-aeb7-ebf1b41e4825'::UUID,
   'listing_alert', '✅ Listing Optimized: LED Desk Lamp (SEO 94)',
   'LED Desk Lamp listing SEO score improved to 94/100. Estimated +14% organic traffic in 30 days.',
   '/listings', '{"listing_id": "B0LEDLAMP01", "seo_score": 94, "traffic_lift_est": 14}'::jsonb,
   false, NOW() - INTERVAL '4 hours'),

  -- Read notifications (older)
  ('nn000008-0000-0000-0000-000000000008'::UUID,
   '8e63fa3b-4d49-4943-aeb7-ebf1b41e4825'::UUID,
   'agent_complete', '🤖 Agent Complete: Competitor Analysis',
   'Competitor analysis for Bamboo Cutting Board complete. Found 6 weaknesses in top competitors. View report.',
   '/competitors', '{"agent": "competitor", "product": "Bamboo Cutting Board", "weaknesses_found": 6}'::jsonb,
   true, NOW() - INTERVAL '8 hours'),

  ('nn000009-0000-0000-0000-000000000009'::UUID,
   '8e63fa3b-4d49-4943-aeb7-ebf1b41e4825'::UUID,
   'ppc_alert', '✅ PPC Optimized: Campaigns Updated',
   'AI adjusted bids on 4 campaigns. Projected ACoS improvement: 24.6% → 19.8%. Estimated +$890/mo revenue.',
   '/ppc', '{"campaigns_updated": 4, "projected_acos": 19.8, "revenue_lift": 890}'::jsonb,
   true, NOW() - INTERVAL '1 hour'),

  ('nn000010-0000-0000-0000-000000000010'::UUID,
   '8e63fa3b-4d49-4943-aeb7-ebf1b41e4825'::UUID,
   'supplier_alert', '📦 Supplier Quote Updated: FitGear',
   'Yiwu FitGear sent new quote for Resistance Bands: $2.95/unit (was $3.10). MOQ 800 (was 1000). Valid 30 days.',
   '/suppliers', '{"supplier": "FitGear", "new_cost": 2.95, "old_cost": 3.10, "new_moq": 800}'::jsonb,
   true, NOW() - INTERVAL '1 day'),

  ('nn000011-0000-0000-0000-000000000011'::UUID,
   '8e63fa3b-4d49-4943-aeb7-ebf1b41e4825'::UUID,
   'trend_alert', '📈 Trend Detected: Home Gym Equipment Under $50',
   'Google Trends shows 41% growth in "home gym under $50". Your Resistance Bands are perfectly positioned.',
   '/trends', '{"trend": "Home Gym Equipment Under $50", "growth": 41}'::jsonb,
   true, NOW() - INTERVAL '2 days'),

  ('nn000012-0000-0000-0000-000000000012'::UUID,
   '8e63fa3b-4d49-4943-aeb7-ebf1b41e4825'::UUID,
   'system', '🔗 Amazon Marketplace Connected',
   'Your Amazon Seller Central account was successfully connected. Syncing products, orders, and PPC data now.',
   '/settings', '{"marketplace": "amazon", "status": "connected"}'::jsonb,
   true, NOW() - INTERVAL '5 days');
