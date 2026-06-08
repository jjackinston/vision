"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { useMutation } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer, Tooltip } from "recharts";
import { cn } from "@/lib/utils";
import { TrendingUp, AlertTriangle } from "lucide-react";

const CATEGORIES = ["home_kitchen", "sports_outdoors", "health_beauty", "electronics", "clothing", "pets", "toys", "office"];

export function SaturationRadarCard({ marketplace }: { marketplace: string }) {
  const [category, setCategory] = useState("home_kitchen");
  const [result, setResult] = useState<any>(null);

  const mutation = useMutation({
    mutationFn: () => api.searchProducts({ query: "", marketplace }).then(() =>
      fetch(`/api/v1/products/saturation-radar?category=${category}&marketplace=${marketplace}`)
        .then(r => r.json())
    ),
  });

  const radarData = result ? [
    { metric: "Current Saturation", value: result.current_saturation_score ?? 45 },
    { metric: "3M Forecast", value: result.saturation_3m ?? 52 },
    { metric: "6M Forecast", value: result.saturation_6m ?? 61 },
    { metric: "Entry Risk", value: result.entry_risk_score ?? 48 },
    { metric: "Exit Risk", value: result.exit_risk_score ?? 38 },
    { metric: "PPC Inflation", value: 55 },
  ] : [];

  return (
    <div className="space-y-6">
      <div className="bg-[#111218] border border-white/5 rounded-xl p-5">
        <div className="flex items-center gap-2 mb-4">
          <TrendingUp className="w-4 h-4 text-blue-400" />
          <h3 className="text-sm font-semibold text-white">Market Saturation Radar</h3>
          <span className="text-xs text-white/30">Module 3</span>
        </div>
        <p className="text-xs text-white/40 mb-4">
          Predict future market overcrowding before entering a category.
        </p>

        <div className="flex flex-wrap gap-2 mb-5">
          {CATEGORIES.map((cat) => (
            <button key={cat} onClick={() => setCategory(cat)}
              className={cn("px-3 py-1 rounded-full text-xs border capitalize transition-all",
                category === cat
                  ? "bg-blue-500/20 border-blue-500/40 text-blue-300"
                  : "bg-white/3 border-white/8 text-white/40 hover:text-white")}>
              {cat.replace("_", " ")}
            </button>
          ))}
        </div>

        <Button onClick={() => mutation.mutateAsync().then(setResult)}
          disabled={mutation.isPending}
          className="bg-blue-600 hover:bg-blue-500 w-full h-9 text-sm">
          {mutation.isPending ? "Analyzing..." : "Analyze Saturation"}
        </Button>
      </div>

      {result && (
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
          className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Radar chart */}
          <div className="bg-[#111218] border border-white/5 rounded-xl p-5">
            <p className="text-xs font-semibold text-white/40 mb-3">Saturation Metrics</p>
            <ResponsiveContainer width="100%" height={220}>
              <RadarChart data={radarData}>
                <PolarGrid stroke="rgba(255,255,255,0.05)" />
                <PolarAngleAxis dataKey="metric" tick={{ fontSize: 10, fill: "rgba(255,255,255,0.4)" }} />
                <Radar dataKey="value" stroke="#3B82F6" fill="#3B82F6" fillOpacity={0.2} strokeWidth={2} />
              </RadarChart>
            </ResponsiveContainer>
          </div>

          {/* Timeline */}
          <div className="bg-[#111218] border border-white/5 rounded-xl p-5">
            <p className="text-xs font-semibold text-white/40 mb-4">Saturation Timeline</p>
            <div className="space-y-3">
              {[
                { label: "Today", score: result.current_saturation_score ?? 45 },
                { label: "3 Months", score: result.saturation_3m ?? 52 },
                { label: "6 Months", score: result.saturation_6m ?? 61 },
                { label: "12 Months", score: result.saturation_12m ?? 74 },
              ].map(({ label, score }) => {
                const color = score < 40 ? "bg-emerald-500" : score < 65 ? "bg-amber-500" : "bg-red-500";
                return (
                  <div key={label} className="flex items-center gap-3">
                    <span className="text-xs text-white/40 w-20 flex-shrink-0">{label}</span>
                    <div className="flex-1 bg-white/5 rounded-full h-2">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${score}%` }}
                        transition={{ duration: 0.6, ease: "easeOut" }}
                        className={`h-2 rounded-full ${color}`}
                      />
                    </div>
                    <span className="text-xs font-semibold text-white w-8 text-right">{score}</span>
                  </div>
                );
              })}
            </div>
            <div className="mt-4 pt-4 border-t border-white/5">
              <p className="text-xs text-white/30 mb-1">Recommendation</p>
              <p className="text-sm text-white font-medium">{result.recommendation ?? "Enter within 60 days before saturation peaks"}</p>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
}
