-- Seed sales_analytics for the PREVIOUS 30-day period (days 30–59)
-- Slightly lower volumes (~87%) so revenue_change shows ~+15% growth
-- Run: psql -h localhost -U sellervision -d sellervision -f seed_analytics_prev.sql

DO $$
DECLARE
  d INTEGER;
  ts TIMESTAMPTZ;
  units INT;
  price NUMERIC;
  gross NUMERIC;
  cogs NUMERIC;
  fees NUMERIC;
  ads NUMERIC;
  refunds NUMERIC;
  net NUMERIC;
BEGIN

FOR d IN 30..59 LOOP
  ts := NOW() - (d || ' days')::INTERVAL;

  -- Bamboo Cutting Board Set ($34.99, Amazon) — ~87% of current volume
  units := 8 + (random() * 7)::INT;
  price := 34.99;
  gross := units * price;
  cogs := gross * 0.32;
  fees := gross * 0.15;
  ads  := gross * 0.115;
  refunds := gross * 0.022;
  net  := gross - cogs - fees - ads - refunds;
  INSERT INTO sales_analytics (id, time, product_id, marketplace, orders, units_sold, gross_revenue, cogs, platform_fees, ad_spend, refunds, net_profit, roi)
  VALUES (gen_random_uuid(), ts, 'ebb69f74-421c-4502-bcf5-d6f656b9ba32'::UUID, 'amazon', units - (random()*2)::INT, units, gross, cogs, fees, ads, refunds, net, ROUND((net/NULLIF(cogs,0))::NUMERIC, 4));

  -- Silicone Cooking Utensil Set ($27.99, Amazon)
  units := 10 + (random() * 7)::INT;
  price := 27.99;
  gross := units * price;
  cogs := gross * 0.30;
  fees := gross * 0.15;
  ads  := gross * 0.135;
  refunds := gross * 0.018;
  net  := gross - cogs - fees - ads - refunds;
  INSERT INTO sales_analytics (id, time, product_id, marketplace, orders, units_sold, gross_revenue, cogs, platform_fees, ad_spend, refunds, net_profit, roi)
  VALUES (gen_random_uuid(), ts, 'c2fdcd92-d0ef-4fca-8c0c-dd1c37ecc82f'::UUID, 'amazon', units - (random()*2)::INT, units, gross, cogs, fees, ads, refunds, net, ROUND((net/NULLIF(cogs,0))::NUMERIC, 4));

  -- LED Desk Lamp with USB Charging ($45.99, Amazon)
  units := 5 + (random() * 4)::INT;
  price := 45.99;
  gross := units * price;
  cogs := gross * 0.38;
  fees := gross * 0.15;
  ads  := gross * 0.145;
  refunds := gross * 0.028;
  net  := gross - cogs - fees - ads - refunds;
  INSERT INTO sales_analytics (id, time, product_id, marketplace, orders, units_sold, gross_revenue, cogs, platform_fees, ad_spend, refunds, net_profit, roi)
  VALUES (gen_random_uuid(), ts, '529e4d0e-4127-409f-82dd-0c51f3754086'::UUID, 'amazon', units - (random()*1)::INT, units, gross, cogs, fees, ads, refunds, net, ROUND((net/NULLIF(cogs,0))::NUMERIC, 4));

  -- Resistance Bands Set Heavy Duty ($22.99, Amazon)
  units := 15 + (random() * 9)::INT;
  price := 22.99;
  gross := units * price;
  cogs := gross * 0.28;
  fees := gross * 0.15;
  ads  := gross * 0.105;
  refunds := gross * 0.012;
  net  := gross - cogs - fees - ads - refunds;
  INSERT INTO sales_analytics (id, time, product_id, marketplace, orders, units_sold, gross_revenue, cogs, platform_fees, ad_spend, refunds, net_profit, roi)
  VALUES (gen_random_uuid(), ts, 'b8eee474-507d-4e52-8923-38987f194437'::UUID, 'amazon', units - (random()*2)::INT, units, gross, cogs, fees, ads, refunds, net, ROUND((net/NULLIF(cogs,0))::NUMERIC, 4));

  -- Stainless Steel Water Bottle 32oz ($19.99, Amazon)
  units := 12 + (random() * 9)::INT;
  price := 19.99;
  gross := units * price;
  cogs := gross * 0.25;
  fees := gross * 0.15;
  ads  := gross * 0.125;
  refunds := gross * 0.018;
  net  := gross - cogs - fees - ads - refunds;
  INSERT INTO sales_analytics (id, time, product_id, marketplace, orders, units_sold, gross_revenue, cogs, platform_fees, ad_spend, refunds, net_profit, roi)
  VALUES (gen_random_uuid(), ts, 'da97c78c-1c3d-4c16-9748-ca50b0699809'::UUID, 'amazon', units - (random()*2)::INT, units, gross, cogs, fees, ads, refunds, net, ROUND((net/NULLIF(cogs,0))::NUMERIC, 4));

END LOOP;

END $$;
