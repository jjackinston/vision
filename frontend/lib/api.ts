import axios, { AxiosInstance, AxiosRequestConfig } from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class APIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: `${API_BASE}/api/v1`,
      headers: { "Content-Type": "application/json" },
      timeout: 30000,
    });

    this.client.interceptors.request.use(async (config) => {
      // Attach Clerk token automatically
      if (typeof window !== "undefined") {
        try {
          const token = await (window as any).__clerk?.session?.getToken();
          if (token) config.headers.Authorization = `Bearer ${token}`;
        } catch {}
      }
      return config;
    });

    this.client.interceptors.response.use(
      (res) => res,
      (error) => {
        if (error.response?.status === 401) {
          window.location.href = "/login";
        }
        return Promise.reject(error);
      }
    );
  }

  // Auth / current user
  async getMe() {
    const { data } = await this.client.get("/auth/me");
    return data as { user_id: string; tenant_id: string; role: string };
  }

  // Products
  async searchProducts(params: ProductSearchParams) {
    const { data } = await this.client.post("/products/search", params);
    return data;
  }

  async getProduct(id: string) {
    const { data } = await this.client.get(`/products/${id}`);
    return data;
  }

  async predictSuccess(concept: ProductConcept) {
    const { data } = await this.client.post("/products/predict-success", concept);
    return data;
  }

  async simulateLaunch(params: LaunchSimParams) {
    const { data } = await this.client.post("/products/launch-simulator", params);
    return data;
  }

  async getOpportunityScore(productId: string) {
    const { data } = await this.client.get(`/products/${productId}/opportunity-score`);
    return data;
  }

  async getCompetitorWeaknesses(productId: string) {
    const { data } = await this.client.get(`/products/${productId}/competitor-weaknesses`);
    return data;
  }

  async getCrossPlatformData(productId: string) {
    const { data } = await this.client.get(`/products/${productId}/cross-platform`);
    return data;
  }

  // Keywords
  async researchKeywords(query: string, marketplace: string = "amazon") {
    const { data } = await this.client.get("/keywords/research", { params: { q: query, marketplace } });
    return data;
  }

  async reverseAsin(asin: string) {
    const { data } = await this.client.get(`/keywords/reverse-asin/${asin}`);
    return data;
  }

  async clusterKeywords(keywords: string[]) {
    const { data } = await this.client.post("/keywords/cluster", { keywords });
    return data;
  }

  // Analytics
  async getCEORecommendations() {
    const { data } = await this.client.get("/analytics/ceo-recommendations");
    return data;
  }

  async runDigitalTwinSimulation(params: SimulationParams) {
    const { data } = await this.client.post("/analytics/simulate", params);
    return data;
  }

  async getAnalytics(period: string = "30d", marketplace?: string) {
    const { data } = await this.client.get("/analytics/overview", { params: { period, marketplace } });
    return data;
  }

  async getRevenueSeries(period = "30d", groupBy = "day", marketplace?: string) {
    const { data } = await this.client.get("/analytics/revenue", { params: { period, group_by: groupBy, marketplace } });
    return data;
  }

  async getByPlatform(period = "30d") {
    const { data } = await this.client.get("/analytics/by-platform", { params: { period } });
    return data;
  }

  async getProductMetrics(params?: { product_id?: string; days?: number; marketplace?: string }) {
    const { data } = await this.client.get("/analytics/product-metrics", { params });
    return data;
  }

  async getKeywordMetrics(params?: { keyword_id?: string; days?: number }) {
    const { data } = await this.client.get("/analytics/keyword-metrics", { params });
    return data;
  }

  async getKeywordOpportunities(params?: { category?: string; min_volume?: number; max_difficulty?: number; marketplace?: string }) {
    const { data } = await this.client.get("/keywords/opportunities", { params });
    return data;
  }

  async getTrendingKeywords(marketplace = "amazon", limit = 20) {
    const { data } = await this.client.get("/keywords/trending", { params: { marketplace, limit } });
    return data;
  }

  async getByProduct(period = "30d", limit = 10, sortBy = "revenue") {
    const { data } = await this.client.get("/analytics/by-product", { params: { period, limit, sort_by: sortBy } });
    return data;
  }

  async listProducts(params?: { marketplace?: string; category?: string; tracked?: boolean; limit?: number }) {
    const { data } = await this.client.get("/products/", { params });
    return data;
  }

  // AI Agents
  async getAgents() {
    const { data } = await this.client.get("/agents/");
    return data;
  }

  async getAgentStatuses() {
    const { data } = await this.client.get("/agents/statuses");
    return data;
  }

  async runAgent(agentType: string, context?: object) {
    const { data } = await this.client.post(`/agents/${agentType}/run`, { context: context ?? {} });
    return data;
  }

  async runAllAgents(context?: object) {
    const { data } = await this.client.post("/agents/run-all", { context: context ?? {} });
    return data;
  }

  async getAgentIntelligence() {
    const { data } = await this.client.get("/agents/intelligence");
    return data;
  }

  async getAgentRun(runId: string) {
    const { data } = await this.client.get(`/agents/runs/${runId}`);
    return data;
  }

  // PPC
  async getPPCPerformance(days = 30, marketplace = "amazon") {
    const { data } = await this.client.get("/ppc/performance", { params: { days, marketplace } });
    return data;
  }

  async getPPCCampaigns(marketplace?: string, status?: string) {
    const { data } = await this.client.get("/ppc/campaigns", { params: { marketplace, status } });
    return data;
  }

  async getPPCAIRecommendations(goal = "acos") {
    const { data } = await this.client.get("/ppc/ai-recommendations", { params: { optimization_goal: goal } });
    return data;
  }

  // Competitors
  async getCompetitors(params?: object) {
    const { data } = await this.client.get("/competitors/", { params });
    return data;
  }

  async analyzeCompetitorWeaknesses(asin: string) {
    const { data } = await this.client.post("/competitors/weakness-scan", { asin });
    return data;
  }

  // Suppliers
  async getSuppliers() {
    const { data } = await this.client.get("/suppliers/");
    return data;
  }

  async analyzeSupplier(supplierName: string, country = "CN") {
    const { data } = await this.client.post("/suppliers/analyze", { supplier_name: supplierName, country });
    return data;
  }

  async generateNegotiationScript(supplierId: string) {
    const { data } = await this.client.post(`/suppliers/${supplierId}/negotiation-script`);
    return data;
  }

  // Marketplace (Module 23)
  async getMarketplaceAssets(category?: string, page = 1) {
    const { data } = await this.client.get("/marketplace/assets", { params: { category, page } });
    return data;
  }

  async purchaseAsset(assetId: string) {
    const { data } = await this.client.post(`/marketplace/assets/${assetId}/purchase`);
    return data;
  }

  async publishAsset(assetData: object) {
    const { data } = await this.client.post("/marketplace/assets", assetData);
    return data;
  }

  // Listings
  async getListings(params?: { marketplace?: string; status?: string; min_seo_score?: number }) {
    const { data } = await this.client.get("/listings/", { params });
    return data;
  }

  async generateListing(productData: object, marketplace: string, keywords: string[] = []) {
    const { data } = await this.client.post("/listings/generate", {
      product_data: productData,
      marketplace,
      target_keywords: keywords,
    });
    return data;
  }

  async generateMultiPlatformListings(productData: object, marketplaces: string[]) {
    const { data } = await this.client.post("/listings/generate-multi-platform", {
      product_data: productData,
      marketplaces,
    });
    return data;
  }

  // Inventory
  async getInventory(filters?: object) {
    const { data } = await this.client.get("/inventory/", { params: filters });
    return data;
  }

  async getStockoutPredictions() {
    const { data } = await this.client.get("/inventory/stockout-predictions");
    return data;
  }

  // Trends
  async getTrends(category?: string) {
    const { data } = await this.client.get("/trends/", { params: { category } });
    return data;
  }

  async detectTrends(category: string, sources: string[]) {
    const { data } = await this.client.post("/trends/detect", { category, sources });
    return data;
  }

  async getViralProducts(marketplace = "tiktok") {
    const { data } = await this.client.get("/trends/viral", { params: { marketplace } });
    return data;
  }

  async analyzeSupplierByName(supplierName: string, country = "CN") {
    const { data } = await this.client.post("/suppliers/analyze", { supplier_name: supplierName, country });
    return data;
  }

  async negotiateSupplier(supplierId: string, params: {
    goal?: string;
    current_price?: number;
    target_price?: number;
    current_moq?: number;
    target_moq?: number;
  }) {
    const { data } = await this.client.post("/suppliers/negotiate", {
      supplier_id: supplierId,
      ...params,
    });
    return data;
  }

  async syncInventory() {
    const { data } = await this.client.post("/inventory/sync");
    return data;
  }

  // Profit calculator
  async calculateProfit(params: ProfitParams) {
    const { data } = await this.client.get("/analytics/profit-calculator", { params });
    return data;
  }

  async comparePlatformProfit(params: ProfitParams) {
    const { data } = await this.client.get("/analytics/platform-comparison", { params });
    return data;
  }

  // Voice assistant
  async processVoiceQuery(query: string) {
    const { data } = await this.client.post("/voice-assistant", { query });
    return data;
  }

  // Notifications
  async getNotifications(params?: { unread_only?: boolean; limit?: number }) {
    const { data } = await this.client.get("/notifications/", { params });
    return data;
  }

  async getUnreadCount() {
    const { data } = await this.client.get("/notifications/unread-count");
    return data;
  }

  async markAllRead() {
    const { data } = await this.client.post("/notifications/mark-read");
    return data;
  }

  async markNotificationRead(id: string) {
    const { data } = await this.client.post(`/notifications/${id}/read`);
    return data;
  }

  // Workflows / Automation
  async getWorkflows(params?: { is_active?: boolean }) {
    const { data } = await this.client.get("/automation/workflows", { params });
    return data;
  }

  async getAutomationTemplates() {
    const { data } = await this.client.get("/automation/templates");
    return data;
  }

  async toggleWorkflow(workflowId: string) {
    const { data } = await this.client.put(`/automation/workflows/${workflowId}/toggle`);
    return data;
  }

  // Integrations
  async getIntegrations() {
    const { data } = await this.client.get("/integrations/");
    return data;
  }

  // Billing
  async getPlans() {
    const { data } = await this.client.get("/billing/plans");
    return data;
  }

  async getUsage() {
    const { data } = await this.client.get("/billing/usage");
    return data;
  }

  async getSubscription() {
    const { data } = await this.client.get("/billing/subscription");
    return data;
  }

  /** Creates a Stripe Checkout session. Returns { checkout_url, session_id }. */
  async createCheckoutSession(planId: string) {
    const { data } = await this.client.post(`/billing/checkout?plan_id=${planId}`);
    return data as { checkout_url: string; session_id: string };
  }

  /** Opens Stripe Customer Portal. Returns { portal_url }. */
  async createPortalSession() {
    const { data } = await this.client.post("/billing/portal");
    return data as { portal_url: string };
  }

  async cancelSubscription(atPeriodEnd = true) {
    const { data } = await this.client.post(`/billing/cancel?at_period_end=${atPeriodEnd}`);
    return data;
  }

  /** @deprecated use createCheckoutSession */
  async createSubscription(planId: string, _paymentMethod?: string) {
    return this.createCheckoutSession(planId);
  }
}

export const api = new APIClient();

// Type definitions
export interface ProductSearchParams {
  query: string;
  marketplace?: string;
  category?: string;
  min_price?: number;
  max_price?: number;
  min_monthly_revenue?: number;
}

export interface ProductConcept {
  concept: string;
  category: string;
  cost: number;
  selling_price: number;
  marketplace: string;
}

export interface LaunchSimParams {
  product_cost: number;
  inventory_quantity: number;
  ppc_budget_daily: number;
  selling_price: number;
  marketplace: string;
  target_bsr?: number;
  launch_strategy?: string;
}

export interface SimulationParams {
  scenario_type: "price_change" | "ppc_increase" | "new_product" | "inventory_change";
  parameters: Record<string, any>;
  forecast_months?: number;
}

export interface ProfitParams {
  product_cost: number;
  selling_price: number;
  marketplace: string;
  monthly_units?: number;
  ad_spend_daily?: number;
  shipping_cost?: number;
  category?: string;
}
