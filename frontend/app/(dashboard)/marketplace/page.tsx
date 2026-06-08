"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { motion } from "framer-motion";
import {
  ShoppingBag, Star, Download, TrendingUp, Sparkles, Plus, Filter,
  Search, Brain, Zap, Bot, BarChart3, FileText, Package, DollarSign,
  CheckCircle2, Crown, ArrowRight, Users, Globe,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { toast } from "sonner";

type AssetCategory = "all" | "dashboards" | "agents" | "automations" | "templates" | "prompts" | "models";

const CATEGORIES: { id: AssetCategory; label: string; icon: any; count: number }[] = [
  { id: "all", label: "All Assets", icon: ShoppingBag, count: 142 },
  { id: "dashboards", label: "Dashboards", icon: BarChart3, count: 28 },
  { id: "agents", label: "AI Agents", icon: Bot, count: 34 },
  { id: "automations", label: "Automations", icon: Zap, count: 41 },
  { id: "templates", label: "Templates", icon: FileText, count: 22 },
  { id: "prompts", label: "AI Prompts", icon: Brain, count: 17 },
];

const ASSETS = [
  {
    id: "1",
    title: "Amazon Product Hunter Pro",
    description: "AI agent that scans Amazon daily for emerging products with ACoS < 20% and opportunity score > 75.",
    author: "SellerVision Labs",
    authorVerified: true,
    category: "agents",
    price: 49,
    rating: 4.9,
    reviews: 284,
    downloads: 1840,
    tags: ["Amazon", "Product Research", "AI Agent"],
    featured: true,
    badge: "Top Seller",
  },
  {
    id: "2",
    title: "Multi-Platform Profit Dashboard",
    description: "Real-time profit tracking across Amazon, Walmart, and Shopify with automated cost reconciliation.",
    author: "DataVault Analytics",
    authorVerified: true,
    category: "dashboards",
    price: 29,
    rating: 4.8,
    reviews: 196,
    downloads: 1210,
    tags: ["Profit", "Multi-Platform", "Analytics"],
    featured: true,
    badge: "Popular",
  },
  {
    id: "3",
    title: "PPC Auto-Optimizer Flow",
    description: "n8n automation: pauses keywords > 35% ACoS, increases bids when ROAS > 5×, adds negatives weekly.",
    author: "AutoSeller",
    authorVerified: false,
    category: "automations",
    price: 19,
    rating: 4.7,
    reviews: 143,
    downloads: 920,
    tags: ["PPC", "Automation", "Amazon"],
    featured: false,
    badge: null,
  },
  {
    id: "4",
    title: "Competitor Deep Scanner Agent",
    description: "Monitors top 10 competitors 24/7. Alerts on price changes, new listings, review velocity spikes.",
    author: "IntelEdge AI",
    authorVerified: true,
    category: "agents",
    price: 39,
    rating: 4.8,
    reviews: 167,
    downloads: 780,
    tags: ["Competitors", "Monitoring", "Alerts"],
    featured: false,
    badge: "New",
  },
  {
    id: "5",
    title: "Launch Readiness Checklist",
    description: "50-point product launch checklist template covering listing quality, inventory, PPC, and ranking strategy.",
    author: "LaunchPro",
    authorVerified: true,
    category: "templates",
    price: 0,
    rating: 4.9,
    reviews: 412,
    downloads: 3200,
    tags: ["Launch", "Checklist", "Free"],
    featured: false,
    badge: "Free",
  },
  {
    id: "6",
    title: "Trend Viral Detector Agent",
    description: "Scans TikTok, Reddit, Pinterest, and Amazon simultaneously. Surfaces emerging trends before they peak.",
    author: "TrendBot",
    authorVerified: true,
    category: "agents",
    price: 59,
    rating: 4.6,
    reviews: 98,
    downloads: 560,
    tags: ["Trends", "TikTok", "AI Agent"],
    featured: true,
    badge: "Trending",
  },
  {
    id: "7",
    title: "Negotiation Script Generator",
    description: "AI prompts library: 30+ supplier negotiation scripts for MOQ reduction, price cuts, payment terms.",
    author: "SupplierGuru",
    authorVerified: false,
    category: "prompts",
    price: 15,
    rating: 4.5,
    reviews: 76,
    downloads: 430,
    tags: ["Supplier", "Negotiation", "Prompts"],
    featured: false,
    badge: null,
  },
  {
    id: "8",
    title: "Inventory Reorder Automator",
    description: "Auto-generates purchase orders when stock hits reorder point. Emails supplier. Logs to spreadsheet.",
    author: "StockSync Pro",
    authorVerified: true,
    category: "automations",
    price: 24,
    rating: 4.8,
    reviews: 211,
    downloads: 1100,
    tags: ["Inventory", "Automation", "Reorder"],
    featured: false,
    badge: "Popular",
  },
  {
    id: "9",
    title: "Success Predictor ML Model",
    description: "Trained on 50K product launches. Input any product concept, get success probability with explainable AI.",
    author: "SellerVision Labs",
    authorVerified: true,
    category: "models",
    price: 99,
    rating: 4.9,
    reviews: 52,
    downloads: 280,
    tags: ["ML", "Prediction", "Launch"],
    featured: true,
    badge: "Pro",
  },
];

export default function MarketplacePage() {
  const [activeCategory, setActiveCategory] = useState<AssetCategory>("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [sortBy, setSortBy] = useState<"popular" | "rating" | "newest" | "price">("popular");
  const [purchasedIds, setPurchasedIds] = useState<Set<string>>(new Set());

  const queryClient = useQueryClient();

  const { data: assetsData } = useQuery({
    queryKey: ["marketplace-assets", activeCategory],
    queryFn: () => api.getMarketplaceAssets(activeCategory === "all" ? undefined : activeCategory),
    staleTime: 1000 * 60 * 5,
  });

  const purchaseMutation = useMutation({
    mutationFn: (assetId: string) => api.purchaseAsset(assetId),
    onSuccess: (_: any, assetId: string) => {
      setPurchasedIds((prev) => new Set([...prev, assetId]));
      queryClient.invalidateQueries({ queryKey: ["marketplace-assets"] });
      toast.success("Asset added to your library");
    },
    onError: () => toast.error("Purchase failed — please try again"),
  });

  const publishMutation = useMutation({
    mutationFn: (assetData: object) => api.publishAsset(assetData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["marketplace-assets"] });
      toast.success("Asset published to marketplace");
    },
    onError: () => toast.error("Publish failed — please try again"),
  });

  const liveAssets: typeof ASSETS = Array.isArray((assetsData as any)?.items)
    ? (assetsData as any).items
    : Array.isArray(assetsData)
    ? (assetsData as any)
    : [];
  const allAssets = liveAssets.length > 0 ? liveAssets : ASSETS;

  const categoryCounts = CATEGORIES.map((cat) => ({
    ...cat,
    count: cat.id === "all" ? allAssets.length : allAssets.filter((a) => a.category === cat.id).length,
  }));

  const filtered = allAssets.filter((a) => {
    const matchCategory = activeCategory === "all" || a.category === activeCategory;
    const matchSearch = !searchQuery || a.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      a.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      a.tags.some((t) => t.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchCategory && matchSearch;
  });

  const sorted = [...filtered].sort((a, b) => {
    if (sortBy === "popular") return b.downloads - a.downloads;
    if (sortBy === "rating") return b.rating - a.rating;
    if (sortBy === "price") return a.price - b.price;
    return 0;
  });

  const featured = allAssets.filter((a) => a.featured).slice(0, 3);

  return (
    <div className="p-6 max-w-[1600px] mx-auto">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between mb-8"
      >
        <div>
          <div className="flex items-center gap-2 mb-1">
            <div className="w-6 h-6 rounded-md bg-gradient-to-br from-pink-500 to-violet-500 flex items-center justify-center">
              <ShoppingBag className="w-3.5 h-3.5 text-white" />
            </div>
            <h1 className="text-xl font-bold text-white">SellerVision Marketplace</h1>
            <Badge className="bg-pink-500/20 text-pink-300 border-0 text-xs">
              <Sparkles className="w-2.5 h-2.5 mr-1" />
              {allAssets.length} Assets
            </Badge>
          </div>
          <p className="text-sm text-white/40">
            Community-built dashboards, agents, automations, and templates
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" className="border-white/10 bg-white/5 text-white/60 hover:text-white text-xs">
            <Users className="w-3.5 h-3.5 mr-1.5" />
            My Purchases
          </Button>
          <Button
            size="sm"
            disabled={publishMutation.isPending}
            onClick={() => publishMutation.mutate({ title: "", category: "agents", price: 0 })}
            className="bg-gradient-to-r from-pink-600 to-violet-600 hover:opacity-90 text-xs"
          >
            <Plus className="w-3.5 h-3.5 mr-1.5" />
            {publishMutation.isPending ? "Publishing…" : "Publish Asset"}
          </Button>
        </div>
      </motion.div>

      {/* Featured Row */}
      <div className="mb-8">
        <h2 className="text-xs font-semibold text-white/40 uppercase tracking-widest mb-3">Featured</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {featured.map((asset, i) => (
            <motion.div
              key={asset.id}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.07 }}
              className="relative bg-gradient-to-br from-violet-500/10 to-pink-500/5 border border-violet-500/20 rounded-xl p-5 cursor-pointer hover:border-violet-500/40 transition-all overflow-hidden"
            >
              <div className="absolute top-0 right-0 w-24 h-24 bg-violet-500/5 rounded-full -translate-y-8 translate-x-8" />
              <div className="flex items-start justify-between mb-3">
                <div className="w-9 h-9 rounded-lg bg-violet-500/20 flex items-center justify-center">
                  {asset.category === "agents" ? <Bot className="w-4.5 h-4.5 text-violet-400" /> :
                   asset.category === "dashboards" ? <BarChart3 className="w-4.5 h-4.5 text-blue-400" /> :
                   <Brain className="w-4.5 h-4.5 text-pink-400" />}
                </div>
                {asset.badge && (
                  <Badge className="bg-amber-500/20 text-amber-300 border-0 text-[9px]">
                    <Crown className="w-2.5 h-2.5 mr-1" />
                    {asset.badge}
                  </Badge>
                )}
              </div>
              <h3 className="text-sm font-bold text-white mb-1">{asset.title}</h3>
              <p className="text-xs text-white/50 line-clamp-2 mb-4">{asset.description}</p>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-xs text-white/40">
                  <Star className="w-3 h-3 text-amber-400 fill-amber-400" />
                  <span className="text-amber-400 font-medium">{asset.rating}</span>
                  <span>({asset.reviews})</span>
                </div>
                <span className="text-sm font-bold text-white">
                  {asset.price === 0 ? "Free" : `$${asset.price}`}
                </span>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Search + Filter bar */}
      <div className="flex items-center gap-3 mb-6">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-white/25" />
          <input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search assets..."
            className="w-full bg-white/5 border border-white/8 rounded-lg pl-9 pr-4 py-2 text-sm text-white placeholder:text-white/25 outline-none focus:border-violet-500/50"
          />
        </div>
        <div className="flex gap-1 bg-white/5 rounded-lg p-1">
          {(["popular", "rating", "newest", "price"] as const).map((s) => (
            <button
              key={s}
              onClick={() => setSortBy(s)}
              className={cn(
                "px-3 py-1 rounded-md text-xs font-medium capitalize transition-all",
                sortBy === s ? "bg-violet-600 text-white" : "text-white/40 hover:text-white"
              )}
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      {/* Category tabs */}
      <div className="flex gap-2 mb-6 overflow-x-auto pb-1">
        {categoryCounts.map((cat) => {
          const Icon = cat.icon;
          return (
            <button
              key={cat.id}
              onClick={() => setActiveCategory(cat.id)}
              className={cn(
                "flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-all border",
                activeCategory === cat.id
                  ? "bg-violet-500/20 border-violet-500/40 text-violet-300"
                  : "bg-white/3 border-white/8 text-white/40 hover:text-white hover:border-white/20"
              )}
            >
              <Icon className="w-3.5 h-3.5" />
              {cat.label}
              <span className="text-[10px] opacity-60">({cat.count})</span>
            </button>
          );
        })}
      </div>

      {/* Asset Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {sorted.map((asset, i) => (
          <motion.div
            key={asset.id}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.04 }}
            className="bg-[#111218] border border-white/5 rounded-xl p-5 hover:border-white/15 transition-all cursor-pointer group"
          >
            <div className="flex items-start gap-3 mb-3">
              <div className="w-9 h-9 rounded-lg bg-white/5 flex items-center justify-center flex-shrink-0">
                {asset.category === "agents" ? <Bot className="w-4 h-4 text-violet-400" /> :
                 asset.category === "dashboards" ? <BarChart3 className="w-4 h-4 text-blue-400" /> :
                 asset.category === "automations" ? <Zap className="w-4 h-4 text-amber-400" /> :
                 asset.category === "templates" ? <FileText className="w-4 h-4 text-emerald-400" /> :
                 asset.category === "prompts" ? <Brain className="w-4 h-4 text-pink-400" /> :
                 <Package className="w-4 h-4 text-white/40" />}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-1.5 mb-0.5">
                  <h3 className="text-sm font-semibold text-white truncate group-hover:text-violet-300 transition-colors">
                    {asset.title}
                  </h3>
                  {asset.badge && (
                    <Badge className={cn("text-[9px] border-0 px-1.5 flex-shrink-0",
                      asset.badge === "Free" ? "bg-emerald-500/20 text-emerald-400" :
                      asset.badge === "New" ? "bg-blue-500/20 text-blue-400" :
                      asset.badge === "Pro" ? "bg-amber-500/20 text-amber-400" :
                      "bg-violet-500/20 text-violet-400"
                    )}>
                      {asset.badge}
                    </Badge>
                  )}
                </div>
                <div className="flex items-center gap-1 text-[10px] text-white/30">
                  <span>{asset.author}</span>
                  {asset.authorVerified && <CheckCircle2 className="w-2.5 h-2.5 text-blue-400" />}
                </div>
              </div>
            </div>

            <p className="text-xs text-white/50 line-clamp-2 mb-4">{asset.description}</p>

            <div className="flex flex-wrap gap-1 mb-4">
              {asset.tags.map((tag) => (
                <span key={tag} className="text-[9px] px-1.5 py-0.5 bg-white/5 text-white/30 rounded">
                  {tag}
                </span>
              ))}
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3 text-xs text-white/30">
                <span className="flex items-center gap-1">
                  <Star className="w-3 h-3 text-amber-400 fill-amber-400" />
                  <span className="text-amber-400 font-medium">{asset.rating}</span>
                  <span>({asset.reviews})</span>
                </span>
                <span className="flex items-center gap-1">
                  <Download className="w-3 h-3" />
                  {asset.downloads.toLocaleString()}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-sm font-bold text-white">
                  {asset.price === 0 ? <span className="text-emerald-400">Free</span> : `$${asset.price}`}
                </span>
                <Button
                  size="sm"
                  disabled={purchaseMutation.isPending || purchasedIds.has(asset.id)}
                  onClick={(e) => { e.stopPropagation(); purchaseMutation.mutate(asset.id); }}
                  className={cn("h-7 px-3 text-xs",
                    purchasedIds.has(asset.id)
                      ? "bg-white/10 text-white/40 cursor-default"
                      : asset.price === 0
                      ? "bg-emerald-600 hover:bg-emerald-500"
                      : "bg-violet-600 hover:bg-violet-500"
                  )}
                >
                  {purchasedIds.has(asset.id) ? "Owned" : asset.price === 0 ? "Get" : "Buy"}
                  <ArrowRight className="w-3 h-3 ml-1" />
                </Button>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Creator CTA */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4 }}
        className="mt-10 bg-gradient-to-r from-violet-500/10 via-pink-500/10 to-violet-500/5 border border-violet-500/20 rounded-xl p-8 text-center"
      >
        <Globe className="w-8 h-8 text-violet-400 mx-auto mb-3" />
        <h3 className="text-lg font-bold text-white mb-2">Become a Creator</h3>
        <p className="text-sm text-white/50 max-w-md mx-auto mb-4">
          Publish your dashboards, agents, and automations. Earn revenue every time another seller uses your asset.
        </p>
        <div className="flex items-center justify-center gap-6 text-xs text-white/40 mb-4">
          <span>✓ Keep 80% revenue share</span>
          <span>✓ No listing fees</span>
          <span>✓ Global seller audience</span>
        </div>
        <Button
          disabled={publishMutation.isPending}
          onClick={() => publishMutation.mutate({ title: "", category: "agents", price: 0 })}
          className="bg-gradient-to-r from-violet-600 to-pink-600 hover:opacity-90 text-sm px-6"
        >
          {publishMutation.isPending ? "Publishing…" : "Start Publishing"}
          <ArrowRight className="w-4 h-4 ml-2" />
        </Button>
      </motion.div>
    </div>
  );
}
