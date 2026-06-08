-- Seed sales_analytics with 30 days of realistic daily data
-- Run: psql -h localhost -U sellervision -d sellervision -f seed_analytics.sql

-- Products:
-- ebb69f74 = Bamboo Cutting Board Set   $34.99  ~10-18 orders/day
-- c2fdcd92 = Silicone Cooking Utensil  $27.99  ~12-20 orders/day
-- 529e4d0e = LED Desk Lamp             $45.99  ~6-11 orders/day
-- b8eee474 = Resistance Bands          $22.99  ~15-28 orders/day
-- da97c78c = Water Bottle 32oz         $19.99  ~14-24 orders/day

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

FOR d IN 0..29 LOOP
  ts := NOW() - (d || ' days')::INTERVAL;

  -- Bamboo Cutting Board Set ($34.99, Amazon)
  units := 10 + (random() * 8)::INT;
  price := 34.99;
  gross := units * price;
  cogs := gross * 0.32;
  fees := gross * 0.15;
  ads  := gross * 0.11;
  refunds := gross * 0.02;
  net  := gross - cogs - fees - ads - refunds;
  INSERT INTO sales_analytics (id, time, product_id, marketplace, orders, units_sold, gross_revenue, cogs, platform_fees, ad_spend, refunds, net_profit, roi)
  VALUES (gen_random_uuid(), ts, 'ebb69f74-421c-4502-bcf5-d6f656b9ba32'::UUID, 'amazon', units - (random()*2)::INT, units, gross, cogs, fees, ads, refunds, net, ROUND((net/NULLIF(cogs,0))::NUMERIC, 4));

  -- Silicone Cooking Utensil Set ($27.99, Amazon)
  units := 12 + (random() * 8)::INT;
  price := 27.99;
  gross := units * price;
  cogs := gross * 0.30;
  fees := gross * 0.15;
  ads  := gross * 0.13;
  refunds := gross * 0.015;
  net  := gross - cogs - fees - ads - refunds;
  INSERT INTO sales_analytics (id, time, product_id, marketplace, orders, units_sold, gross_revenue, cogs, platform_fees, ad_spend, refunds, net_profit, roi)
  VALUES (gen_random_uuid(), ts, 'c2fdcd92-d0ef-4fca-8c0c-dd1c37ecc82f'::UUID, 'amazon', units - (random()*2)::INT, units, gross, cogs, fees, ads, refunds, net, ROUND((net/NULLIF(cogs,0))::NUMERIC, 4));

  -- LED Desk Lamp with USB Charging ($45.99, Amazon)
  units := 6 + (random() * 5)::INT;
  price := 45.99;
  gross := units * price;
  cogs := gross * 0.38;
  fees := gross * 0.15;
  ads  := gross * 0.14;
  refunds := gross * 0.025;
  net  := gross - cogs - fees - ads - refunds;
  INSERT INTO sales_analytics (id, time, product_id, marketplace, orders, units_sold, gross_revenue, cogs, platform_fees, ad_spend, refunds, net_profit, roi)
  VALUES (gen_random_uuid(), ts, '529e4d0e-4127-409f-82dd-0c51f3754086'::UUID, 'amazon', units - (random()*1)::INT, units, gross, cogs, fees, ads, refunds, net, ROUND((net/NULLIF(cogs,0))::NUMERIC, 4));

  -- Resistance Bands Set Heavy Duty ($22.99, Amazon)
  units := 18 + (random() * 10)::INT;
  price := 22.99;
  gross := units * price;
  cogs := gross * 0.28;
  fees := gross * 0.15;
  ads  := gross * 0.10;
  refunds := gross * 0.01;
  net  := gross - cogs - fees - ads - refunds;
  INSERT INTO sales_analytics (id, time, product_id, marketplace, orders, units_sold, gross_revenue, cogs, platform_fees, ad_spend, refunds, net_profit, roi)
  VALUES (gen_random_uuid(), ts, 'b8eee474-507d-4e52-8923-38987f194437'::UUID, 'amazon', units - (random()*2)::INT, units, gross, cogs, fees, ads, refunds, net, ROUND((net/NULLIF(cogs,0))::NUMERIC, 4));

  -- Stainless Steel Water Bottle 32oz ($19.99, Amazon)
  units := 14 + (random() * 10)::INT;
  price := 19.99;
  gross := units * price;
  cogs := gross * 0.25;
  fees := gross * 0.15;
  ads  := gross * 0.12;
  refunds := gross * 0.015;
  net  := gross - cogs - fees - ads - refunds;
  INSERT INTO sales_analytics (id, time, product_id, marketplace, orders, units_sold, gross_revenue, cogs, platform_fees, ad_spend, refunds, net_profit, roi)
  VALUES (gen_random_uuid(), ts, 'da97c78c-1c3d-4c16-9748-ca50b0699809'::UUID, 'amazon', units - (random()*2)::INT, units, gross, cogs, fees, ads, refunds, net, ROUND((net/NULLIF(cogs,0))::NUMERIC, 4));

END LOOP;

END $$;
