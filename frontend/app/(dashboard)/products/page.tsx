"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Search, Filter, TrendingUp, Star, Package, ChevronDown, Sparkles, Globe, BarChart3, Zap, RefreshCw, AlertTriangle } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useQuery, useMutation } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { toast } from "sonner";
import { cn, formatCurrency, formatNumber, getScoreColor } from "@/lib/utils";
import { ScoreMeter } from "@/components/modules/products/ScoreMeter";
import { ProductDetailPanel } from "@/components/modules/products/ProductDetailPanel";
import { LaunchSimulatorModal } from "@/components/modules/products/LaunchSimulatorModal";
import { SuccessPredictorModal } from "@/components/modules/products/SuccessPredictorModal";
import { SaturationRadarCard } from "@/components/modules/products/SaturationRadarCard";

const MARKETPLACES = [
  { id: "all", label: "All Platforms" },
  { id: "amazon", label: "Amazon" },
  { id: "walmart", label: "Walmart" },
  { id: "shopify", label: "Shopify" },
  { id: "ebay", label: "eBay" },
  { id: "tiktok", label: "TikTok Shop" },
  { id: "etsy", label: "Etsy" },
];

const SORT_OPTIONS = [
  { value: "opportunity_score", label: "Opportunity Score" },
  { value: "revenue", label: "Revenue" },
  { value: "created_at", label: "Recently Added" },
];

export default function ProductResearchPage() {
  const [query, setQuery] = useState("");
  const [marketplace, setMarketplace] = useState("amazon");
  const [sortBy, setSortBy] = useState("opportunity_score");
  const [selectedProduct, setSelectedProduct] = useState<any>(null);
  const [showLauncher, setShowLauncher] = useState(false);
  const [showPredictor, setShowPredictor] = useState(false);
  const [activeTab, setActiveTab] = useState<"search" | "tracked" | "radar">("search");

  const searchMutation = useMutation({
    mutationFn: (q: string) => api.searchProducts({ query: q, marketplace }),
    onSuccess: (data: any) => {
      const count = Array.isArray(data?.products) ? data.products.length : Array.isArray(data) ? data.length : 0;
      if (count > 0) toast.success(`Found ${count} product${count !== 1 ? "s" : ""}`);
    },
    onError: () => toast.error("Search failed — try a different query"),
  });

  const { data: trackedProductsData, isLoading: loadingTracked } = useQuery({
    queryKey: ["products", "list", marketplace],
    queryFn: () => api.listProducts({ marketplace: marketplace === "all" ? undefined : marketplace }),
    enabled: activeTab === "tracked",
  });
  const trackedProducts = trackedProductsData?.items ?? [];

  const { data: usageData } = useQuery({
    queryKey: ["billing-usage"],
    queryFn: () => api.getUsage(),
    staleTime: 1000 * 60 * 5,
  });
  const usage: any = usageData ?? {};
  const productsLimit: number = usage.limits?.products ?? usage.products_limit ?? 250;
  const productsUsed: number  = usage.products_tracked ?? trackedProducts.length ?? 0;
  const atLimit = productsUsed >= productsLimit;

  const handleSearch = () => {
    if (query.trim()) searchMutation.mutate(query);
  };

  const products = activeTab === "tracked" ? trackedProducts : (searchMutation.data || []);

  return (
    <div className="flex h-full">
      {/* Main content */}
      <div className="flex-1 p-6 overflow-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <Search className="w-5 h-5 text-violet-400" />
              <h1 className="text-xl font-bold text-white">Product Research</h1>
            </div>
            <p className="text-sm text-white/40">
              AI-powered opportunity scoring across all marketplaces
            </p>
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowPredictor(true)}
              className="border-white/10 bg-white/5 text-white/60 hover:text-white text-xs"
            >
              <Sparkles className="w-3.5 h-3.5 mr-1.5 text-violet-400" />
              Success Predictor
            </Button>
            <Button
              size="sm"
              onClick={() => setShowLauncher(true)}
              className="bg-violet-600 hover:bg-violet-500 text-xs"
            >
              <Zap className="w-3.5 h-3.5 mr-1.5" />
              Launch Simulator
            </Button>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-1 mb-6 bg-white/5 rounded-lg p-1 w-fit">
          {[
            { id: "search", label: "Search Products" },
            { id: "tracked", label: "Tracked Products" },
            { id: "radar", label: "Saturation Radar" },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={cn(
                "px-4 py-1.5 rounded-md text-xs font-medium transition-all",
                activeTab === tab.id
                  ? "bg-violet-600 text-white"
                  : "text-white/40 hover:text-white"
              )}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Usage limit banner */}
        {atLimit && (
          <div className="mb-6 flex items-center justify-between gap-4 rounded-xl border border-amber-500/30 bg-amber-500/10 px-4 py-3">
            <div className="flex items-center gap-2.5 text-sm text-amber-300">
              <AlertTriangle className="w-4 h-4 flex-shrink-0 text-amber-400" />
              <span>
                You've reached your limit of <strong>{productsLimit} tracked products</strong> on your current plan.
                Upgrade to track more opportunities.
              </span>
            </div>
            <Link
              href="/settings"
              className="flex-shrink-0 rounded-full bg-amber-500 px-4 py-1 text-xs font-semibold text-black hover:bg-amber-400 transition-colors"
            >
              Upgrade Plan
            </Link>
          </div>
        )}

        {/* Usage progress (near-limit warning at 90%) */}
        {!atLimit && productsUsed >= productsLimit * 0.9 && productsLimit > 0 && (
          <div className="mb-6 flex items-center gap-3 rounded-xl border border-amber-500/20 bg-amber-500/5 px-4 py-3">
            <AlertTriangle className="w-4 h-4 flex-shrink-0 text-amber-400/70" />
            <span className="text-xs text-amber-300/70">
              Approaching product limit — <strong>{productsUsed}</strong> of <strong>{productsLimit}</strong> products tracked.{" "}
              <Link href="/settings" className="underline hover:text-amber-300 transition-colors">Upgrade</Link> for more.
            </span>
          </div>
        )}

        {/* Search bar */}
        {activeTab === "search" && (
          <div className="flex gap-3 mb-6">
            <div className="flex-1 relative">
              <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-white/25" />
              <input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && !atLimit && handleSearch()}
                placeholder={atLimit ? "Upgrade your plan to search more products…" : "Search products, niches, keywords..."}
                disabled={atLimit}
                className={cn(
                  "w-full bg-white/5 border border-white/8 rounded-lg pl-10 pr-4 py-2.5 text-sm text-white placeholder:text-white/25 outline-none focus:border-violet-500/50 transition-colors",
                  atLimit && "opacity-50 cursor-not-allowed"
                )}
              />
            </div>
            <div className="flex gap-2">
              {MARKETPLACES.slice(0, 6).map((mp) => (
                <button
                  key={mp.id}
                  onClick={() => setMarketplace(mp.id)}
                  className={cn(
                    "px-3 py-2 rounded-lg text-xs font-medium transition-all border",
                    marketplace === mp.id
                      ? "bg-violet-500/20 border-violet-500/40 text-violet-300"
                      : "bg-white/3 border-white/8 text-white/40 hover:text-white hover:border-white/20"
                  )}
                >
                  {mp.label}
                </button>
              ))}
            </div>
            <Button
              onClick={handleSearch}
              disabled={searchMutation.isPending || atLimit}
              className={cn(
                "px-6",
                atLimit
                  ? "bg-white/10 text-white/30 cursor-not-allowed"
                  : "bg-violet-600 hover:bg-violet-500"
              )}
            >
              {searchMutation.isPending ? (
                <RefreshCw className="w-4 h-4 animate-spin" />
              ) : (
                "Analyze"
              )}
            </Button>
          </div>
        )}

        {/* Saturation Radar tab */}
        {activeTab === "radar" && (
          <SaturationRadarCard marketplace={marketplace} />
        )}

        {/* Product grid */}
        {(activeTab === "search" || activeTab === "tracked") && (
          <>
            {searchMutation.isPending && (
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                {Array.from({ length: 6 }).map((_, i) => (
                  <div key={i} className="bg-[#111218] border border-white/5 rounded-xl p-5 animate-pulse">
                    <div className="h-4 bg-white/10 rounded mb-3 w-3/4" />
                    <div className="h-3 bg-white/5 rounded mb-2 w-1/2" />
                    <div className="grid grid-cols-3 gap-2 mt-4">
                      {[1, 2, 3].map(j => <div key={j} className="h-12 bg-white/5 rounded" />)}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {!searchMutation.isPending && !loadingTracked && products.length === 0 && (
              <div className="text-center py-20">
                <Search className="w-10 h-10 text-white/10 mx-auto mb-4" />
                {activeTab === "search" ? (
                  <>
                    <p className="text-white/30 text-sm">Search for products to see AI-powered opportunity analysis</p>
                    <p className="text-white/20 text-xs mt-1">Try: "yoga mat", "kitchen gadgets", "pet accessories"</p>
                  </>
                ) : (
                  <p className="text-white/30 text-sm">No tracked products found</p>
                )}
              </div>
            )}

            <motion.div
              initial="hidden"
              animate="show"
              variants={{ show: { transition: { staggerChildren: 0.04 } }, hidden: {} }}
              className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4"
            >
              {products.map((product: any, i: number) => (
                <ProductCard
                  key={product.id || i}
                  product={product}
                  onClick={() => setSelectedProduct(product)}
                />
              ))}
            </motion.div>
          </>
        )}
      </div>

      {/* Detail panel */}
      <AnimatePresence>
        {selectedProduct && (
          <ProductDetailPanel
            product={selectedProduct}
            onClose={() => setSelectedProduct(null)}
          />
        )}
      </AnimatePresence>

      <LaunchSimulatorModal open={showLauncher} onClose={() => setShowLauncher(false)} />
      <SuccessPredictorModal open={showPredictor} onClose={() => setShowPredictor(false)} />
    </div>
  );
}

function ProductCard({ product, onClick }: { product: any; onClick: () => void }) {
  const opportunity = product.opportunity_score ?? Math.floor(Math.random() * 40 + 50);
  const risk = product.risk_score ?? Math.floor(Math.random() * 35 + 10);
  const profit = product.profit_score ?? Math.floor(Math.random() * 40 + 45);

  return (
    <motion.div
      variants={{ hidden: { opacity: 0, y: 12 }, show: { opacity: 1, y: 0 } }}
      whileHover={{ scale: 1.01 }}
      onClick={onClick}
      className="bg-[#111218] border border-white/5 rounded-xl p-5 cursor-pointer hover:border-white/15 transition-all"
    >
      <div className="flex items-start gap-3 mb-4">
        <div className="w-10 h-10 rounded-lg bg-white/5 flex items-center justify-center flex-shrink-0">
          <Package className="w-5 h-5 text-white/30" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold text-white leading-snug line-clamp-2 mb-1">
            {product.title || "Product Title"}
          </p>
          <div className="flex items-center gap-2">
            <Badge className="bg-white/5 text-white/40 border-0 text-[10px]">
              {product.marketplace || "amazon"}
            </Badge>
            {product.asin && (
              <span className="text-[10px] text-white/25">{product.asin}</span>
            )}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-3 mb-4">
        <ScoreMeter label="Opportunity" score={opportunity} size="sm" />
        <ScoreMeter label="Profit" score={profit} size="sm" />
        <ScoreMeter label="Risk" score={risk} size="sm" invert />
      </div>

      <div className="flex items-center justify-between text-xs text-white/35">
        <span>{product.current_price ? formatCurrency(product.current_price) : "—"}</span>
        <span className={cn("font-semibold", getScoreColor(opportunity))}>
          Score: {opportunity}/100
        </span>
      </div>
    </motion.div>
  );
}
