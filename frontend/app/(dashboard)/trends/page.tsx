"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Lightbulb, TrendingUp, Flame, Clock, RefreshCw, ExternalLink } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useQuery, useMutation } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";
import { toast } from "sonner";

const SOURCES = ["google", "tiktok", "reddit", "pinterest", "youtube"];
const CATEGORIES = ["all", "home", "beauty", "fitness", "kitchen", "tech", "pets", "fashion", "food"];

export default function TrendsPage() {
  const [selectedSources, setSelectedSources] = useState<string[]>(["google", "tiktok", "reddit"]);
  const [category, setCategory] = useState("all");
  const [detectResult, setDetectResult] = useState<any>(null);

  const { data: emerging, isLoading } = useQuery({
    queryKey: ["emerging-trends"],
    queryFn: () => api.getTrends(category !== "all" ? category : undefined),
    placeholderData: { items: SAMPLE_TRENDS },
  });

  const { data: viral } = useQuery({
    queryKey: ["viral-products"],
    queryFn: () => api.getViralProducts("tiktok"),
    placeholderData: SAMPLE_VIRAL,
  });

  const detectMutation = useMutation({
    mutationFn: () => api.detectTrends(category !== "all" ? category : "", selectedSources),
    onSuccess: (data) => {
      setDetectResult(data);
      toast.success("Trend scan complete");
    },
    onError: () => toast.error("Trend detection failed — try again"),
  });

  const toggleSource = (s: string) =>
    setSelectedSources(prev => prev.includes(s) ? prev.filter(x => x !== s) : [...prev, s]);

  const trends = (emerging as any)?.items ?? SAMPLE_TRENDS;

  return (
    <div className="p-6 max-w-[1400px] mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Lightbulb className="w-5 h-5 text-amber-400" />
            <h1 className="text-xl font-bold text-white">Trend Discovery</h1>
            <Badge className="bg-amber-500/20 text-amber-400 border-0 text-xs">Module 14</Badge>
            <Badge className="bg-red-500/20 text-red-400 border-0 text-xs">
              <Flame className="w-2.5 h-2.5 mr-1" /> Live
            </Badge>
          </div>
          <p className="text-sm text-white/40">
            Real-time trend detection across Google, TikTok, Reddit, Pinterest, YouTube
          </p>
        </div>
      </div>

      {/* Detection controls */}
      <div className="bg-[#111218] border border-white/5 rounded-xl p-5 mb-6">
        <div className="flex flex-wrap items-center gap-4">
          <div>
            <p className="text-[10px] uppercase text-white/30 font-semibold mb-2">Sources</p>
            <div className="flex gap-2">
              {SOURCES.map((s) => (
                <button key={s} onClick={() => toggleSource(s)}
                  className={cn("px-3 py-1 rounded-full text-xs border capitalize transition-all",
                    selectedSources.includes(s)
                      ? "bg-amber-500/20 border-amber-500/40 text-amber-300"
                      : "bg-white/3 border-white/8 text-white/40 hover:text-white")}>
                  {s}
                </button>
              ))}
            </div>
          </div>
          <div>
            <p className="text-[10px] uppercase text-white/30 font-semibold mb-2">Category</p>
            <div className="flex flex-wrap gap-2">
              {CATEGORIES.map((c) => (
                <button key={c} onClick={() => setCategory(c)}
                  className={cn("px-3 py-1 rounded-full text-xs border capitalize transition-all",
                    category === c ? "bg-white/15 border-white/30 text-white" : "bg-white/3 border-white/8 text-white/40 hover:text-white")}>
                  {c}
                </button>
              ))}
            </div>
          </div>
          <Button onClick={() => detectMutation.mutate()} disabled={detectMutation.isPending}
            className="ml-auto bg-amber-500 hover:bg-amber-400 text-black font-semibold">
            {detectMutation.isPending
              ? <><RefreshCw className="w-3.5 h-3.5 mr-1.5 animate-spin" />Scanning...</>
              : <><Lightbulb className="w-3.5 h-3.5 mr-1.5" />Detect Trends</>}
          </Button>
        </div>
      </div>

      {/* Detection results */}
      {detectResult?.trends && (
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="mb-6">
          <h3 className="text-sm font-semibold text-white mb-3">
            Detected {detectResult.trends.length} trends
            {detectResult.top_opportunity && (
              <span className="ml-2 text-amber-400 font-normal text-xs">Top: {detectResult.top_opportunity}</span>
            )}
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {detectResult.trends.map((t: any, i: number) => (
              <TrendCard key={i} trend={t} index={i} />
            ))}
          </div>
        </motion.div>
      )}

      {/* Existing trends */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <h3 className="text-sm font-semibold text-white mb-3">
            Emerging Trends
            {isLoading && <RefreshCw className="w-3.5 h-3.5 inline ml-2 animate-spin text-white/30" />}
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {trends.map((t: any, i: number) => (
              <TrendCard key={i} trend={t} index={i} />
            ))}
          </div>
        </div>

        {/* Viral products sidebar */}
        <div>
          <h3 className="text-sm font-semibold text-white mb-3">
            <Flame className="w-4 h-4 inline text-red-400 mr-1" />
            Going Viral on TikTok
          </h3>
          <div className="space-y-2">
            {(SAMPLE_VIRAL as any[]).map((v: any, i: number) => (
              <div key={i} className="bg-[#111218] border border-white/5 rounded-xl p-3">
                <div className="flex items-center justify-between mb-1">
                  <p className="text-xs font-semibold text-white">{v.product_name}</p>
                  <Badge className="bg-red-500/20 text-red-400 border-0 text-[9px]">
                    🔥 {v.viral_score}
                  </Badge>
                </div>
                <p className="text-[10px] text-white/40">{v.category}</p>
                <div className="flex items-center gap-3 mt-2 text-[10px] text-white/35">
                  <span>{v.growth_rate_percent}% growth</span>
                  <span>{v.best_selling_price_range}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function TrendCard({ trend, index }: { trend: any; index: number }) {
  const score = trend.trend_score ?? trend.viral_score ?? 70;
  const color = score >= 75 ? "emerald" : score >= 50 ? "amber" : "white";
  const colorMap = { emerald: "text-emerald-400 bg-emerald-500/10", amber: "text-amber-400 bg-amber-500/10", white: "text-white/60 bg-white/5" };

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index * 0.04 }}
      className="bg-[#111218] border border-white/5 rounded-xl p-4 hover:border-white/15 transition-colors">
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <p className="text-sm font-semibold text-white mb-1">{trend.topic}</p>
          <div className="flex items-center gap-2">
            {trend.source && (
              <Badge className="bg-white/5 text-white/40 border-0 text-[9px] capitalize">{trend.source}</Badge>
            )}
            {trend.category && (
              <Badge className="bg-white/5 text-white/40 border-0 text-[9px] capitalize">{trend.category}</Badge>
            )}
          </div>
        </div>
        <div className={cn("text-sm font-bold px-2 py-1 rounded-lg flex-shrink-0", colorMap[color as keyof typeof colorMap])}>
          {score}
        </div>
      </div>
      <div className="grid grid-cols-2 gap-2 mb-3 text-xs">
        <div>
          <span className="text-white/30">Momentum</span>
          <span className="text-white ml-1 font-medium">{trend.momentum_score ?? "—"}</span>
        </div>
        <div>
          <span className="text-white/30">Lifespan</span>
          <span className="text-white ml-1 font-medium capitalize">{(trend.lifespan_prediction ?? "seasonal")?.replace("_", " ")}</span>
        </div>
        <div>
          <span className="text-white/30">Entry</span>
          <span className="text-white ml-1 font-medium capitalize">{(trend.entry_window ?? "now")?.replace("_", " ")}</span>
        </div>
        <div>
          <span className="text-white/30">Opportunity</span>
          <span className={cn("ml-1 font-medium capitalize",
            trend.commercial_opportunity === "high" ? "text-emerald-400" : trend.commercial_opportunity === "medium" ? "text-amber-400" : "text-white/50")}>
            {trend.commercial_opportunity ?? "medium"}
          </span>
        </div>
      </div>
      {trend.related_products?.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {trend.related_products.slice(0, 3).map((p: string, i: number) => (
            <span key={i} className="text-[9px] bg-white/5 text-white/35 px-1.5 py-0.5 rounded-full">{p}</span>
          ))}
        </div>
      )}
    </motion.div>
  );
}

const SAMPLE_TRENDS = [
  { topic: "Stanley Cup Alternatives", source: "tiktok", category: "kitchen", trend_score: 88, momentum_score: 92, lifespan_prediction: "sustained", entry_window: "now", commercial_opportunity: "high", related_products: ["Quencher Tumbler", "Insulated Cup"] },
  { topic: "Mushroom Coffee", source: "google", category: "health", trend_score: 76, momentum_score: 84, lifespan_prediction: "seasonal", entry_window: "now", commercial_opportunity: "high", related_products: ["Lion's Mane Coffee", "Chaga Blend"] },
  { topic: "Weighted Blankets Kids", source: "reddit", category: "home", trend_score: 71, momentum_score: 68, lifespan_prediction: "evergreen", entry_window: "3_months", commercial_opportunity: "medium", related_products: ["Sensory Blanket", "Calm Blanket"] },
  { topic: "AI Pet Cameras", source: "pinterest", category: "pets", trend_score: 82, momentum_score: 79, lifespan_prediction: "sustained", entry_window: "now", commercial_opportunity: "high", related_products: ["Smart Pet Monitor", "Treat Dispenser"] },
];

const SAMPLE_VIRAL = [
  { product_name: "Cloud Slippers", category: "Fashion", viral_score: 94, growth_rate_percent: 340, best_selling_price_range: "$25-$45" },
  { product_name: "Mini Waffle Maker", category: "Kitchen", viral_score: 88, growth_rate_percent: 220, best_selling_price_range: "$20-$35" },
  { product_name: "Collagen Gummies", category: "Beauty", viral_score: 85, growth_rate_percent: 185, best_selling_price_range: "$18-$30" },
  { product_name: "Posture Corrector 2.0", category: "Health", viral_score: 81, growth_rate_percent: 167, best_selling_price_range: "$22-$40" },
];
