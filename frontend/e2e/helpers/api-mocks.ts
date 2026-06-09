/**
 * Reusable Playwright route interceptors for all SellerVision AI API calls.
 *
 * Usage in a test:
 *   import { mockAllApis, mockProducts } from "./helpers/api-mocks";
 *   await mockAllApis(page);           // sensible defaults for smoke tests
 *   await mockProducts(page, { items: [], total: 0 });  // override products
 */

import type { Page, Route } from "@playwright/test";

// ── Fixture data ───────────────────────────────────────────────────────
export const FIXTURES = {
  me: {
    user_id: "22222222-2222-2222-2222-222222222222",
    tenant_id: "11111111-1111-1111-1111-111111111111",
    role: "owner",
    email: "dev@sellervision.local",
    full_name: "Dev Seller",
  },

  tenant: {
    id: "11111111-1111-1111-1111-111111111111",
    slug: "dev-seller",
    name: "Dev Seller Co",
    plan: "Professional",
    is_active: true,
    trial_ends_at: null,
    settings: { onboarding_complete: false },
    stripe_customer_id: null,
    stripe_subscription_id: null,
  },

  products: {
    items: [
      {
        id: "p1", asin: "B08N5WRWNW", title: "Wireless Earbuds Pro",
        marketplace: "amazon", opportunity_score: 87, ai_score: 91,
        monthly_revenue: 45200, monthly_units: 380, price: 119.99,
        bsr: 1240, review_count: 4382, avg_rating: 4.6,
        category: "Electronics", is_tracked: true,
      },
      {
        id: "p2", asin: "B09XNKG5LM", title: "Bamboo Cutting Board Set",
        marketplace: "amazon", opportunity_score: 74, ai_score: 79,
        monthly_revenue: 12800, monthly_units: 320, price: 39.99,
        bsr: 8450, review_count: 1201, avg_rating: 4.4,
        category: "Kitchen", is_tracked: true,
      },
    ],
    total: 2,
    page: 1,
    per_page: 25,
  },

  searchProducts: {
    products: [
      {
        id: "ps1", asin: "B07QFL2QBK", title: "Laptop Stand Adjustable",
        marketplace: "amazon", opportunity_score: 82, monthly_revenue: 32000,
        price: 29.99, bsr: 3100, review_count: 8923, avg_rating: 4.7,
      },
    ],
    total: 1,
  },

  analytics: {
    revenue: 142500, revenue_change: 12.4,
    profit: 38400, profit_change: 8.7,
    units: 1840, units_change: 15.2,
    roas: 4.2, roas_change: -3.1,
    sessions: 24800, conversion_rate: 7.4,
    top_marketplace: "amazon",
  },

  revenueSeries: {
    labels: ["Jun 1", "Jun 2", "Jun 3", "Jun 4", "Jun 5", "Jun 6", "Jun 7"],
    datasets: [
      { label: "Revenue", data: [18000, 22000, 19500, 24000, 21000, 26500, 28000] },
    ],
  },

  inventory: {
    items: [
      {
        id: "inv1", product_id: "p1", asin: "B08N5WRWNW", sku: "WE-PRO-01",
        quantity_on_hand: 145, quantity_reserved: 20, reorder_point: 100,
        reorder_quantity: 500, unit_cost: 18.5, warehouse: "FBA-US-EAST",
        days_of_stock: 28, stockout_risk: "low",
      },
    ],
    total: 1,
  },

  keywords: {
    items: [
      {
        id: "kw1", keyword: "wireless earbuds", search_volume: 245000,
        competition: "high", cpc: 1.42, opportunity_score: 72,
        trend: "rising", marketplace: "amazon",
      },
      {
        id: "kw2", keyword: "noise cancelling earbuds", search_volume: 89000,
        competition: "medium", cpc: 1.18, opportunity_score: 84,
        trend: "stable", marketplace: "amazon",
      },
    ],
    total: 2,
  },

  billing: {
    subscription: null as string | null,
    plan: "Professional",
    status: "trialing",
    trial_ends_at: new Date(Date.now() + 7 * 86400000).toISOString() as string | null,
    current_period_end: null as string | null,
  },

  plans: [
    {
      id: "plan-starter", name: "Starter", price: 49, currency: "usd",
      billing_interval: "month", is_active: true,
      features: ["50 products", "5 AI agents", "Email reports"],
    },
    {
      id: "plan-professional", name: "Professional", price: 149, currency: "usd",
      billing_interval: "month", is_active: true, is_popular: true,
      features: ["250 products", "15 AI agents", "PPC automation", "API access"],
    },
    {
      id: "plan-business", name: "Business", price: 349, currency: "usd",
      billing_interval: "month", is_active: true,
      features: ["1000 products", "Unlimited agents", "Custom reports"],
    },
    {
      id: "plan-agency", name: "Agency", price: 799, currency: "usd",
      billing_interval: "month", is_active: true,
      features: ["Unlimited products", "White-label", "Dedicated support"],
    },
  ],

  usage: {
    products_tracked: 2, limits: { products: 250 },
    products_limit: 250, agents_used: 0, agents_limit: 15,
  },

  agents: {
    items: [
      {
        id: "agent1", name: "Price Optimizer", type: "pricing",
        status: "idle", last_run: null, tasks_completed: 0,
      },
    ],
    total: 1,
  },

  agentStatuses: [
    { agent_type: "pricing", status: "idle", last_run: null },
    { agent_type: "seo", status: "idle", last_run: null },
  ],

  competitors: {
    items: [
      {
        id: "comp1", asin: "B07PXVMK7G", title: "Competitor Earbuds",
        price: 89.99, bsr: 980, review_count: 12450, avg_rating: 4.3,
        marketplace: "amazon", tracked_since: "2026-01-01",
      },
    ],
    total: 1,
  },

  trends: {
    items: [
      {
        keyword: "wireless earbuds 2026", trend_score: 92,
        search_volume: 320000, growth_rate: 24.5,
        status: "rising", marketplace: "amazon",
      },
    ],
    total: 1,
  },

  ppc: {
    total_spend: 3240, total_revenue: 13650, roas: 4.21,
    campaigns: [
      {
        id: "camp1", name: "Wireless Earbuds - Auto", status: "enabled",
        spend: 1820, revenue: 7640, roas: 4.2, impressions: 45000,
        clicks: 920, acos: 23.8,
      },
    ],
    total: 1,
  },

  suppliers: {
    items: [
      {
        id: "sup1", name: "Shenzhen Electronics Co.", country: "CN",
        rating: 4.8, lead_time_days: 25, min_order_qty: 500,
        categories: ["Electronics"],
      },
    ],
    total: 1,
  },

  listings: {
    items: [
      {
        id: "lst1", product_id: "p1", asin: "B08N5WRWNW",
        title: "Wireless Earbuds Pro — Active Noise Cancelling",
        optimization_score: 78, seo_score: 82, conversion_score: 74,
        marketplace: "amazon", status: "active",
      },
    ],
    total: 1,
  },

  automation: {
    rules: [
      {
        id: "rule1", name: "Auto-reprice when BSR drops", type: "pricing",
        status: "active", trigger: "bsr_change", actions_count: 2,
        last_triggered: "2026-06-05T14:30:00Z",
      },
    ],
    total: 1,
  },

  marketplace: {
    connections: [],
    available: [
      { id: "amazon", name: "Amazon", logo: "/logos/amazon.svg", connected: false },
      { id: "walmart", name: "Walmart", logo: "/logos/walmart.svg", connected: false },
    ],
  },

  notifications: { items: [], total: 0, unread: 0 },

  adminStats: {
    tenants: { total: 3, active: 3, paying: 1, new_30d: 2, trial: 2 },
    users: { total: 5 },
    products: { total: 8 },
    plan_distribution: { Professional: 2, Starter: 1 },
  },

  adminTenants: {
    items: [
      {
        id: "11111111-1111-1111-1111-111111111111",
        slug: "dev-seller", name: "Dev Seller Co",
        plan: "Professional", is_active: true,
        trial_ends_at: null, stripe_customer_id: null,
        stripe_subscription_id: null,
        member_count: 1, product_count: 2, created_at: "2026-01-01T00:00:00Z",
      },
    ],
    total: 1, page: 1, per_page: 20,
  },

  adminUsers: {
    items: [
      {
        id: "22222222-2222-2222-2222-222222222222",
        email: "dev@sellervision.local", full_name: "Dev Seller",
        clerk_id: null, is_active: true, tenant: "dev-seller",
        role: "owner", last_login: null, created_at: "2026-01-01T00:00:00Z",
      },
    ],
    total: 1, page: 1, per_page: 20,
  },
};

// ── Route helpers ──────────────────────────────────────────────────────

/** Intercept a URL pattern and respond with JSON. */
export async function mockRoute(
  page: Page,
  pattern: string | RegExp,
  body: unknown,
  status = 200,
) {
  await page.route(pattern, (route: Route) => {
    route.fulfill({
      status,
      contentType: "application/json",
      body: JSON.stringify(body),
    });
  });
}

/** Register all API mocks with sensible defaults. Call this at the start of each test. */
export async function mockAllApis(page: Page, overrides: Partial<typeof FIXTURES> = {}) {
  const F = { ...FIXTURES, ...overrides };
  const base = "**/api/v1";

  // Auth
  await mockRoute(page, `${base}/auth/me`, F.me);
  await mockRoute(page, `${base}/auth/sync`, F.me);

  // Tenant — mock both /me (legacy) and /current (real backend routes)
  await mockRoute(page, `${base}/tenants/me`, F.tenant);
  await mockRoute(page, `${base}/tenants/current`, F.tenant);
  await mockRoute(page, `${base}/tenants/me/settings`, { settings: {} });
  await mockRoute(page, `${base}/tenants/current/settings`, { settings: {} });
  await mockRoute(page, `${base}/tenants/current/members`, []);
  await mockRoute(page, `${base}/auth/api-keys`, []);

  // Products
  await mockRoute(page, `${base}/products/`, F.products);
  await mockRoute(page, `${base}/products/search`, F.searchProducts);
  await mockRoute(page, new RegExp(`${base}/products/[^/]+$`), F.products.items[0]);
  await mockRoute(page, `${base}/products/predict-success`, { score: 82, confidence: "high", insights: [] });
  await mockRoute(page, `${base}/products/launch-simulator`, { projected_units: 420, projected_revenue: 50000 });

  // Analytics
  await mockRoute(page, `${base}/analytics/overview`, F.analytics);
  await mockRoute(page, `${base}/analytics/revenue`, F.revenueSeries);
  await mockRoute(page, `${base}/analytics/profit`, F.revenueSeries);
  await mockRoute(page, `${base}/analytics/ceo-briefing`, { summary: "Strong week. Revenue up 12%.", recommendations: [] });

  // Inventory
  await mockRoute(page, `${base}/inventory/`, F.inventory);
  await mockRoute(page, `${base}/inventory/warehouses`, { items: [{ id: "w1", name: "FBA-US-EAST", type: "fba" }], total: 1 });

  // Keywords
  await mockRoute(page, `${base}/keywords/`, F.keywords);
  await mockRoute(page, `${base}/keywords/research`, F.keywords);

  // Billing
  await mockRoute(page, `${base}/billing/subscription`, F.billing);
  await mockRoute(page, `${base}/billing/plans`, F.plans);
  await mockRoute(page, `${base}/billing/usage`, F.usage);
  await mockRoute(page, `${base}/billing/checkout`, { checkout_url: "https://checkout.stripe.com/test", session_id: "cs_test_123" });

  // Agents
  await mockRoute(page, `${base}/agents/`, F.agents);
  await mockRoute(page, `${base}/agents/statuses`, F.agentStatuses);

  // Competitors
  await mockRoute(page, `${base}/competitors/`, F.competitors);

  // Trends
  await mockRoute(page, `${base}/trends/`, F.trends);

  // PPC
  await mockRoute(page, `${base}/ppc/`, F.ppc);
  await mockRoute(page, `${base}/ppc/campaigns`, F.ppc);

  // Suppliers
  await mockRoute(page, `${base}/suppliers/`, F.suppliers);

  // Listings
  await mockRoute(page, `${base}/listings/`, F.listings);

  // Automation
  await mockRoute(page, `${base}/automation/`, F.automation);
  await mockRoute(page, `${base}/automation/rules`, F.automation);

  // Marketplace integrations
  await mockRoute(page, `${base}/marketplace/`, F.marketplace);
  await mockRoute(page, `${base}/integrations/`, F.marketplace);

  // Notifications
  await mockRoute(page, `${base}/notifications/`, F.notifications);

  // Admin
  await mockRoute(page, `${base}/admin/stats`, F.adminStats);
  await mockRoute(page, `${base}/admin/tenants`, F.adminTenants);
  await mockRoute(page, `${base}/admin/users`, F.adminUsers);
  await mockRoute(page, `${base}/admin/audit-logs`, { items: [], total: 0, page: 1, per_page: 50 });
  await mockRoute(page, new RegExp(`${base}/admin/tenants/[^/]+$`), F.adminTenants.items[0]);
}
