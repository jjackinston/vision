"use client";

import { motion } from "framer-motion";
import { X, ExternalLink, TrendingUp, Target, Package, Star, BarChart3, Globe, Brain } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScoreMeter } from "./ScoreMeter";
import { cn, formatCurrency } from "@/lib/utils";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

interface ProductDetailPanelProps {
  product: any;
  onClose: () => void;
}

export function ProductDetailPanel({ product, onClose }: ProductDetailPanelProps) {
  const { data: crossPlatform } = useQuery({
    queryKey: ["cross-platform", product.id],
    queryFn: () => product.id ? api.getCrossPlatformData(product.id) : null,
    enabled: !!product.id,
  });

  const scores = [
    { label: "Opportunity", score: product.opportunity_score ?? 78 },
    { label: "Profit", score: product.profit_score ?? 72 },
    { label: "Competition", score: product.competition_score ?? 45, invert: true },
    { label: "Risk", score: product.risk_score ?? 28, invert: true },
    { label: "Entry", score: product.market_entry_score ?? 65 },
  ];

  return (
    <motion.div
      initial={{ x: "100%", opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      exit={{ x: "100%", opacity: 0 }}
      transition={{ type: "spring", damping: 30, stiffness: 300 }}
      className="w-96 border-l border-white/5 bg-[#0D0E12] flex flex-col overflow-hidden flex-shrink-0"
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-white/5">
        <div className="flex items-center gap-2">
          <Brain className="w-4 h-4 text-violet-400" />
          <span className="text-sm font-semibold text-white">AI Analysis</span>
        </div>
        <button onClick={onClose} className="text-white/30 hover:text-white transition-colors">
          <X className="w-4 h-4" />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-5">
        {/* Product info */}
        <div>
          <div className="flex items-center gap-2 mb-2">
            <Badge className="bg-violet-500/20 text-violet-300 border-0 text-[10px]">
              {product.marketplace || "amazon"}
            </Badge>
            {product.asin && (
              <span className="text-[10px] text-white/30">{product.asin}</span>
            )}
          </div>
          <h3 className="text-sm font-semibold text-white leading-snug mb-2">
            {product.title || "Product Title"}
          </h3>
          <div className="flex items-center gap-3 text-xs text-white/40">
            <span>{product.current_price ? formatCurrency(product.current_price) : "—"}</span>
            <span>•</span>
            <span>{product.category || "Category"}</span>
          </div>
        </div>

        {/* Score meters */}
        <div>
          <p className="text-[10px] font-semibold uppercase text-white/30 mb-3">AI Scores</p>
          <div className="grid grid-cols-5 gap-2">
            {scores.map((s) => (
              <ScoreMeter key={s.label} {...s} size="sm" />
            ))}
          </div>
        </div>

        {/* Predictions */}
        <div className="bg-white/3 border border-white/8 rounded-xl p-4">
          <p className="text-[10px] font-semibold uppercase text-white/30 mb-3">Revenue Predictions</p>
          <div className="space-y-2.5">
            {[
              { label: "30-day units", value: product.prediction_30d_units ?? 120 },
              { label: "90-day units", value: product.prediction_90d_units ?? 380 },
              { label: "12-month revenue", value: product.prediction_12m_revenue ? formatCurrency(product.prediction_12m_revenue) : "$48,000" },
            ].map((row) => (
              <div key={row.label} className="flex items-center justify-between">
                <span className="text-xs text-white/40">{row.label}</span>
                <span className="text-xs font-semibold text-white">{row.value}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Cross-platform */}
        {crossPlatform?.comparison && (
          <div>
            <p className="text-[10px] font-semibold uppercase text-white/30 mb-3">
              Cross-Platform Analysis
            </p>
            <div className="space-y-2">
              {Object.entries(crossPlatform.comparison).map(([mp, data]: [string, any]) => (
                <div key={mp} className="flex items-center justify-between bg-white/3 rounded-lg px-3 py-2">
                  <span className="text-xs text-white/50 capitalize">{mp}</span>
                  <span className="text-xs text-white font-medium">
                    {data.monthly_sales ? `${data.monthly_sales} sales/mo` : data.note || "—"}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* AI reasoning */}
        {product.reasoning && (
          <div className="bg-violet-500/8 border border-violet-500/20 rounded-xl p-4">
            <p className="text-[10px] font-semibold uppercase text-violet-400 mb-2">AI Reasoning</p>
            <p className="text-xs text-white/60 leading-relaxed">{product.reasoning}</p>
          </div>
        )}

        {/* Action */}
        {product.action_recommendation && (
          <div className="bg-emerald-500/8 border border-emerald-500/20 rounded-xl p-4">
            <p className="text-[10px] font-semibold uppercase text-emerald-400 mb-1">Recommendation</p>
            <p className="text-xs text-white/70">{product.action_recommendation}</p>
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="p-4 border-t border-white/5 space-y-2">
        <Button className="w-full bg-violet-600 hover:bg-violet-500 text-sm h-9">
          Track This Product
        </Button>
        <Button variant="outline" className="w-full border-white/10 bg-white/5 text-white/60 hover:text-white text-sm h-9">
          <Globe className="w-3.5 h-3.5 mr-2" />
          View Cross-Platform Data
        </Button>
      </div>
    </motion.div>
  );
}
