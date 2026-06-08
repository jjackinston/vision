-- Seed trends, competitors, and listings tables
-- Products already in DB:
--   ebb69f74 = Bamboo Cutting Board Set
--   c2fdcd92 = Silicone Cooking Utensil Set
--   529e4d0e = LED Desk Lamp
--   b8eee474 = Resistance Bands
--   da97c78c = Water Bottle 32oz

-- ============================================================
-- TRENDS (8 rows — emerging trends across categories)
-- ============================================================
INSERT INTO trends (topic, source, category, trend_score, momentum_score, viral_score,
                    lifespan_prediction, related_products, data_points, ai_analysis, detected_at)
VALUES
  ('Bamboo Kitchen Products', 'google', 'kitchen', 87, 72, 65,
   '6-12 months',
   ARRAY['bamboo cutting board', 'bamboo utensils', 'bamboo storage'],
   '{"search_volume": 320000, "growth_rate": 34, "cpc": 1.42}'::jsonb,
   '{"opportunity": "High", "saturation": "Low", "recommended_action": "Launch bamboo kitchen bundle"}'::jsonb,
   NOW() - INTERVAL '2 days'),

  ('Stanley Cup Dupe Water Bottles', 'tiktok', 'drinkware', 96, 91, 98,
   '3-6 months',
   ARRAY['40oz tumbler', 'insulated water bottle', 'hydration bottle'],
   '{"search_volume": 890000, "growth_rate": 340, "cpc": 2.10}'::jsonb,
   '{"opportunity": "Very High", "saturation": "Medium", "recommended_action": "Differentiate on color/lid design"}'::jsonb,
   NOW() - INTERVAL '1 day'),

  ('Resistance Band Workouts', 'google', 'fitness', 78, 65, 55,
   '12-24 months',
   ARRAY['resistance bands set', 'home gym equipment', 'workout bands'],
   '{"search_volume": 450000, "growth_rate": 18, "cpc": 1.85}'::jsonb,
   '{"opportunity": "Medium", "saturation": "Medium", "recommended_action": "Bundle with workout guide PDF"}'::jsonb,
   NOW() - INTERVAL '3 days'),

  ('LED Desk Lamp Home Office', 'google', 'tech', 82, 68, 44,
   '12-18 months',
   ARRAY['led desk lamp', 'usb charging lamp', 'adjustable desk light'],
   '{"search_volume": 280000, "growth_rate": 22, "cpc": 1.65}'::jsonb,
   '{"opportunity": "High", "saturation": "Low", "recommended_action": "Target WFH segment with USB-C charging"}'::jsonb,
   NOW() - INTERVAL '4 days'),

  ('Silicone Cooking Utensil Sets', 'reddit', 'kitchen', 71, 58, 42,
   '18-24 months',
   ARRAY['silicone spatula set', 'non-stick utensils', 'heat resistant cooking tools'],
   '{"search_volume": 195000, "growth_rate": 15, "cpc": 1.20}'::jsonb,
   '{"opportunity": "Medium", "saturation": "Medium", "recommended_action": "Focus on color variety and gift bundling"}'::jsonb,
   NOW() - INTERVAL '5 days'),

  ('Eco-Friendly Kitchen Accessories', 'pinterest', 'kitchen', 75, 62, 70,
   '24+ months',
   ARRAY['reusable food bags', 'beeswax wraps', 'bamboo products'],
   '{"search_volume": 165000, "growth_rate": 28, "cpc": 0.95}'::jsonb,
   '{"opportunity": "High", "saturation": "Low", "recommended_action": "Emphasize sustainability credentials"}'::jsonb,
   NOW() - INTERVAL '6 days'),

  ('TikTok Made Me Buy It Kitchen', 'tiktok', 'kitchen', 93, 88, 95,
   '2-4 months',
   ARRAY['viral kitchen gadgets', 'as seen on tiktok', 'tiktok kitchen tools'],
   '{"search_volume": 720000, "growth_rate": 285, "cpc": 2.40}'::jsonb,
   '{"opportunity": "Very High", "saturation": "Low", "recommended_action": "Create TikTok-ready unboxing content"}'::jsonb,
   NOW() - INTERVAL '12 hours'),

  ('Home Gym Equipment Under $50', 'google', 'fitness', 84, 76, 60,
   '6-12 months',
   ARRAY['resistance bands', 'yoga mat', 'dumbbells', 'jump rope'],
   '{"search_volume": 380000, "growth_rate": 41, "cpc": 2.15}'::jsonb,
   '{"opportunity": "High", "saturation": "Medium", "recommended_action": "Position as affordable gym replacement"}'::jsonb,
   NOW() - INTERVAL '2 days');


-- ============================================================
-- COMPETITORS (12 rows — 2-3 per product)
-- ============================================================
INSERT INTO competitors (product_id, asin, marketplace, seller_id, brand, title,
                         price, review_count, review_rating, monthly_sales, monthly_revenue,
                         weakness_analysis, threat_level, tracked_since)
VALUES
  -- Bamboo Cutting Board competitors
  ('ebb69f74-421c-4502-bcf5-d6f656b9ba32'::UUID,
   'B07QX9LMBK', 'amazon', 'A1B2C3D4E5F6G7', 'BambooKing',
   'BambooKing Professional Cutting Board Set with Juice Groove',
   32.99, 4820, 4.2, 1240, 40960.80,
   '{"weaknesses": [{"type": "durability", "issue": "Cracks after 6 months per 18% of reviews"}, {"type": "packaging", "issue": "Arrives damaged frequently"}], "opportunities": ["Stronger construction", "Better packaging"]}'::jsonb,
   'high', NOW() - INTERVAL '30 days'),

  ('ebb69f74-421c-4502-bcf5-d6f656b9ba32'::UUID,
   'B08ABC2222', 'amazon', 'A2B3C4D5E6F7G8', 'EcoKitchen',
   'EcoKitchen Organic Bamboo Cutting Board 3-Piece Set',
   27.99, 2100, 4.4, 890, 24921.10,
   '{"weaknesses": [{"type": "size", "issue": "Smaller than advertised per 22% reviews"}, {"type": "odor", "issue": "Slight smell when new"}], "opportunities": ["Accurate sizing photos", "Odor-free treatment"]}'::jsonb,
   'medium', NOW() - INTERVAL '25 days'),

  ('ebb69f74-421c-4502-bcf5-d6f656b9ba32'::UUID,
   'B09DEF3333', 'amazon', 'A3B4C5D6E7F8G9', 'NaturalCo',
   'NaturalCo Premium Bamboo Cutting Board with Handles',
   35.99, 5600, 4.6, 1890, 68022.10,
   '{"weaknesses": [{"type": "price", "issue": "Customers say overpriced for quality"}, {"type": "care", "issue": "High maintenance per instructions"}], "opportunities": ["Lower price point", "Easy care design"]}'::jsonb,
   'high', NOW() - INTERVAL '20 days'),

  -- Resistance Bands competitors
  ('b8eee474-507d-4e52-8923-38987f194437'::UUID,
   'B08GY5H7T1', 'amazon', 'A4B5C6D7E8F9G0', 'FitElite',
   'FitElite Resistance Bands Set 5 Levels Heavy Duty',
   19.99, 8420, 4.1, 3200, 63968.00,
   '{"weaknesses": [{"type": "snap", "issue": "Bands snap under heavy use per 31% reviews"}, {"type": "door_anchor", "issue": "Door anchor breaks easily"}], "opportunities": ["Reinforced latex", "Metal door anchor"]}'::jsonb,
   'high', NOW() - INTERVAL '28 days'),

  ('b8eee474-507d-4e52-8923-38987f194437'::UUID,
   'B07YMHBRJ7', 'amazon', 'A5B6C7D8E9F0G1', 'PowerBands',
   'PowerBands Professional Workout Resistance Bands',
   24.99, 3150, 4.5, 1100, 27489.00,
   '{"weaknesses": [{"type": "guide", "issue": "No exercise guide included"}, {"type": "carry_bag", "issue": "Bag tears after few uses"}], "opportunities": ["Include digital guide", "Reinforced storage bag"]}'::jsonb,
   'medium', NOW() - INTERVAL '22 days'),

  -- Water Bottle competitors
  ('da97c78c-1c3d-4c16-9748-ca50b0699809'::UUID,
   'B08H8JHTJZ', 'amazon', 'A6B7C8D9E0F1G2', 'HydroMax',
   'HydroMax 32oz Stainless Steel Water Bottle Insulated',
   21.99, 6740, 4.3, 2800, 61572.00,
   '{"weaknesses": [{"type": "lid_leak", "issue": "Lid leaks when tilted per 24% reviews"}, {"type": "coating", "issue": "Paint chips after 3 months"}], "opportunities": ["Leak-proof lid design", "Powder coat finish"]}'::jsonb,
   'high', NOW() - INTERVAL '15 days'),

  ('da97c78c-1c3d-4c16-9748-ca50b0699809'::UUID,
   'B09KLM4567', 'amazon', 'A7B8C9D0E1F2G3', 'ClearFlow',
   'ClearFlow Wide Mouth Water Bottle Stainless Steel',
   16.99, 1890, 4.0, 740, 12572.60,
   '{"weaknesses": [{"type": "insulation", "issue": "Does not keep cold 24h as advertised"}, {"type": "cleaning", "issue": "Hard to clean interior"}], "opportunities": ["True 24h insulation", "Wide mouth with cleaning brush"]}'::jsonb,
   'low', NOW() - INTERVAL '18 days'),

  -- LED Desk Lamp competitors
  ('529e4d0e-4127-409f-82dd-0c51f3754086'::UUID,
   'B08MWPQ8N3', 'amazon', 'A8B9C0D1E2F3G4', 'LumiDesk',
   'LumiDesk LED Desk Lamp with USB-A Charging 5 Color Modes',
   42.99, 3280, 4.2, 980, 42130.20,
   '{"weaknesses": [{"type": "usb_speed", "issue": "USB charging very slow per 35% reviews"}, {"type": "flicker", "issue": "Light flickers at low brightness"}], "opportunities": ["USB-C fast charging", "Flicker-free driver"]}'::jsonb,
   'medium', NOW() - INTERVAL '12 days'),

  ('529e4d0e-4127-409f-82dd-0c51f3754086'::UUID,
   'B07N1BRQDJ', 'amazon', 'A9B0C1D2E3F4G5', 'BrightWork',
   'BrightWork Architect Desk Lamp Adjustable LED',
   55.99, 1640, 4.6, 420, 23515.80,
   '{"weaknesses": [{"type": "price", "issue": "Too expensive for features offered"}, {"type": "assembly", "issue": "Difficult assembly instructions"}], "opportunities": ["Better value at $40-45", "Tool-free assembly"]}'::jsonb,
   'low', NOW() - INTERVAL '10 days'),

  -- Silicone Utensil competitors
  ('c2fdcd92-d0ef-4fca-8c0c-dd1c37ecc82f'::UUID,
   'B08CXPQ4R2', 'amazon', 'B0C1D2E3F4G5H6', 'SiliCook',
   'SiliCook Premium Silicone Cooking Utensil Set 14-Piece',
   24.99, 5120, 4.3, 1650, 41233.50,
   '{"weaknesses": [{"type": "handle", "issue": "Handle gets hot during cooking"}, {"type": "melt", "issue": "Tips melt near open flame"}], "opportunities": ["Insulated handle", "Higher heat rating"]}'::jsonb,
   'high', NOW() - INTERVAL '14 days'),

  ('c2fdcd92-d0ef-4fca-8c0c-dd1c37ecc82f'::UUID,
   'B09RST7890', 'amazon', 'B1C2D3E4F5G6H7', 'KitchenPro',
   'KitchenPro Silicone Spatula Set BPA Free Heat Resistant',
   18.99, 2340, 4.1, 760, 14432.40,
   '{"weaknesses": [{"type": "color", "issue": "Color fades quickly per 28% reviews"}, {"type": "holder", "issue": "No utensil holder included"}], "opportunities": ["Color-fast materials", "Include magnetic holder"]}'::jsonb,
   'medium', NOW() - INTERVAL '8 days'),

  ('c2fdcd92-d0ef-4fca-8c0c-dd1c37ecc82f'::UUID,
   'B08UVW1234', 'amazon', 'B2C3D4E5F6G7H8', 'ChefSelect',
   'ChefSelect Professional Kitchen Utensil Set with Stand',
   32.99, 890, 4.7, 310, 10226.90,
   '{"weaknesses": [{"type": "stock", "issue": "Frequently out of stock"}, {"type": "price", "issue": "Higher priced than alternatives with same quality"}], "opportunities": ["Reliable inventory", "Competitive pricing at $25-28"]}'::jsonb,
   'low', NOW() - INTERVAL '5 days');


-- ============================================================
-- LISTINGS (5 rows — one live listing per product)
-- ============================================================
INSERT INTO listings (product_id, marketplace, external_id, title, bullet_points,
                      description, backend_keywords, price, status, seo_score,
                      completeness_score, ai_generated, published_at)
VALUES
  ('ebb69f74-421c-4502-bcf5-d6f656b9ba32'::UUID,
   'amazon', 'B0BAMBOO001',
   'Bamboo Cutting Board Set of 3 | Eco-Friendly Kitchen Prep Boards with Juice Grooves & Handles | 100% Organic Bamboo | Dishwasher Safe',
   ARRAY[
     'PREMIUM ORGANIC BAMBOO — Made from 100% Moso bamboo, naturally antibacterial and 16% harder than maple wood. Resists knife scarring and odors.',
     'DEEP JUICE GROOVES — Wide channels around the perimeter catch all juices from meat, fruits, and vegetables. Keeps your counters clean.',
     'ERGONOMIC HANDLES — Built-in handles make it easy to transfer chopped ingredients directly to the pot or pan without mess.',
     'THREE SIZES FOR EVERY TASK — Large 18"×12" for meat, medium 14"×10" for veggies, small 10"×7" for fruits and cheese. Stacks neatly.',
     'EASY CARE — Hand wash recommended; condition monthly with mineral oil. Includes care instructions and food-safe conditioning oil sample.'
   ],
   'Upgrade your kitchen prep with our professional-grade bamboo cutting board set. Crafted from sustainably harvested Moso bamboo, these boards are naturally antimicrobial, making them safer than plastic and more durable than wood. The set of three boards covers every cutting task from meal prep to charcuterie boards.',
   ARRAY['bamboo cutting board', 'cutting board set', 'organic bamboo board', 'kitchen prep board', 'juice groove cutting board', 'eco friendly cutting board', 'wooden cutting board'],
   34.99, 'active', 91.5, 96.0, true, NOW() - INTERVAL '45 days'),

  ('c2fdcd92-d0ef-4fca-8c0c-dd1c37ecc82f'::UUID,
   'amazon', 'B0SILICOOK01',
   'Silicone Cooking Utensil Set 14-Piece | BPA-Free Heat Resistant 480°F | Non-Scratch Kitchen Tools with Stainless Steel Core',
   ARRAY[
     'COMPLETE 14-PIECE SET — Includes spatulas, spoons, ladle, tongs, whisk, pasta server, and slotted turner. Everything you need for daily cooking.',
     'BPA-FREE & FOOD SAFE — Made from premium food-grade silicone, 100% BPA-free. Safe for all cookware including non-stick, cast iron, and stainless steel.',
     'HEAT RESISTANT TO 480°F — Won''t melt, warp, or discolor near high heat. Stainless steel internal core prevents bending under pressure.',
     'NON-SCRATCH DESIGN — Soft silicone heads protect your expensive non-stick and ceramic cookware from scratching and damage.',
     'ERGONOMIC HANDLES — Comfortable non-slip grip handles stay cool during cooking. Hanging loops for easy storage or display.'
   ],
   'Cook smarter with our complete silicone utensil set. Designed for serious home cooks who demand tools that work hard and last. Each utensil features a stainless steel core wrapped in premium food-grade silicone for strength and flexibility.',
   ARRAY['silicone cooking utensils', 'kitchen utensil set', 'bpa free cooking tools', 'non scratch spatula', 'heat resistant utensils', 'silicone spatula set', 'cooking spoon set'],
   27.99, 'active', 88.0, 93.5, true, NOW() - INTERVAL '38 days'),

  ('529e4d0e-4127-409f-82dd-0c51f3754086'::UUID,
   'amazon', 'B0LEDLAMP01',
   'LED Desk Lamp with USB-C & USB-A Charging Ports | 5 Color Modes 10 Brightness Levels | Touch Control | Eye-Care Technology | Home Office',
   ARRAY[
     'DUAL USB CHARGING — Built-in USB-C (18W fast charge) and USB-A ports. Charge your phone, tablet, or laptop while you work. No extra adapter needed.',
     'EYE-CARE TECHNOLOGY — Flicker-free light with CRI >90 accurately renders colors. Reduces eye strain during long work or study sessions.',
     '5 COLOR MODES × 10 BRIGHTNESS — Warm (3000K), Natural (4000K), Cool (5000K), Reading, and Night modes. 10 brightness levels for perfect lighting.',
     'FLEXIBLE GOOSENECK DESIGN — 360° rotating base and fully adjustable gooseneck arm. Direct light exactly where you need it on your desk.',
     'TOUCH & MEMORY CONTROL — Tap to on/off, hold to dim. Remembers your last settings. Auto-off timer at 30/60 minutes to save energy.'
   ],
   'Transform your home office or study space with professional-grade LED lighting. Engineered for productivity with flicker-free technology and a full spectrum of color temperatures to match any task or time of day.',
   ARRAY['led desk lamp', 'desk lamp usb charging', 'office desk lamp', 'study lamp', 'eye care desk light', 'adjustable desk lamp', 'touch control lamp'],
   45.99, 'active', 94.0, 97.5, true, NOW() - INTERVAL '52 days'),

  ('b8eee474-507d-4e52-8923-38987f194437'::UUID,
   'amazon', 'B0RESBANDS1',
   'Resistance Bands Set 5 Levels | Heavy Duty Latex Loop Bands for Home Gym | Pilates Yoga CrossFit | Includes Carry Bag & Exercise Guide',
   ARRAY[
     '5 RESISTANCE LEVELS — Yellow (10lb), Red (20lb), Black (30lb), Purple (40lb), Green (50lb). Progressive resistance for all fitness levels from beginner to advanced.',
     'HEAVY DUTY LATEX — Crafted from 100% natural latex, 3× thicker than standard bands. Snap-proof design tested to 2,000+ stretch cycles without degradation.',
     'COMPLETE HOME GYM — Use for squats, deadlifts, pull-ups, chest press, lateral walks, and 50+ exercises. Replaces thousands in gym equipment.',
     '12-PAGE EXERCISE GUIDE — Full-color printed guide with 30 exercises and 4-week beginner workout program. QR code links to 60-minute video workout.',
     'COMPACT & PORTABLE — Fits in the included mesh carry bag the size of a water bottle. Take your workout anywhere — hotel, park, or office.'
   ],
   'Build strength, improve flexibility, and tone your body with professional resistance bands. Used by physical therapists, personal trainers, and athletes worldwide. Our heavy-duty latex formula provides smooth, consistent resistance throughout the full range of motion.',
   ARRAY['resistance bands', 'workout bands', 'exercise bands set', 'loop resistance bands', 'home gym bands', 'pilates resistance bands', 'yoga bands'],
   22.99, 'active', 89.5, 95.0, true, NOW() - INTERVAL '41 days'),

  ('da97c78c-1c3d-4c16-9748-ca50b0699809'::UUID,
   'amazon', 'B0WATERBOTL1',
   'Stainless Steel Water Bottle 32oz | Triple Insulated | Leak-Proof Lid | Keeps Cold 24H Hot 12H | BPA-Free Wide Mouth Bottle',
   ARRAY[
     'TRIPLE WALL INSULATION — Three-layer vacuum insulation keeps beverages ice cold 24 hours or steaming hot 12 hours. Sweating-free exterior.',
     'LEAK-PROOF GUARANTEED — Military-grade 360° seal lid with locking mechanism. Toss it in your gym bag with confidence.',
     'WIDE MOUTH FOR ICE — 2.2-inch opening fits standard ice cubes. Easy to fill, drink, and clean. Compatible with most water purification tablets.',
     'FOOD-GRADE STAINLESS — 18/8 food-grade stainless steel interior. No plastic taste or smell. BPA-free, phthalate-free, and toxin-free.',
     'LIFETIME WARRANTY — We stand behind every bottle. Full replacement warranty, no questions asked. Includes: bottle, leak-proof lid, sports lid, cleaning brush.'
   ],
   'Stay hydrated all day with the last water bottle you''ll ever need. Our triple-insulated design outperforms competitors at every price point. Whether you''re hiking, working out, or commuting, your drinks stay at the perfect temperature all day.',
   ARRAY['stainless steel water bottle', '32oz water bottle', 'insulated water bottle', 'leak proof water bottle', 'bpa free water bottle', 'wide mouth water bottle', 'gym water bottle'],
   19.99, 'active', 92.5, 98.0, true, NOW() - INTERVAL '35 days');
