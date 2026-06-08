"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { DollarSign, TrendingUp, BarChart3 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useMutation } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { cn, formatCurrency } from "@/lib/utils";

const MARKETPLACES = ["amazon", "walmart", "shopify", "ebay", "tiktok", "etsy"];

export default function ProfitCalculatorPage() {
  const [form, setForm] = useState({
    product_cost: 5.00,
    selling_price: 29.99,
    marketplace: "amazon",
    monthly_units: 100,
    ad_spend_daily: 20,
    shipping_cost: 1.50,
    category: "home",
  });
  const [compareAll, setCompareAll] = useState(false);

  const calcMutation = useMutation({
    mutationFn: () => api.calculateProfit(form),
  });

  const compareMutation = useMutation({
    mutationFn: () => api.comparePlatformProfit(form),
  });

  const result = calcMutation.data as any;
  const comparison = compareMutation.data as any[];

  const field = (key: keyof typeof form, label: string, type = "number", prefix = "") => (
    <div>
      <label className="text-[10px] font-semibold uppercase text-white/30 block mb-1.5">{label}</label>
      <div className="relative">
        {prefix && <span className="absolute left-3 top-1/2 -translate-y-1/2 text-white/30 text-sm">{prefix}</span>}
        <input type={type} value={(form as any)[key]}
          onChange={(e) => setForm(p => ({ ...p, [key]: type === "number" ? parseFloat(e.target.value) || 0 : e.target.value }))}
          className={`w-full bg-white/5 border border-white/10 rounded-lg py-2.5 text-sm text-white outline-none focus:border-violet-500/50 ${prefix ? "pl-7 pr-3" : "px-3"}`}
        />
      </div>
    </div>
  );

  return (
    <div className="p-6 max-w-[1400px] mx-auto">
      <div className="flex items-center gap-2 mb-6">
        <DollarSign className="w-5 h-5 text-emerald-400" />
        <h1 className="text-xl font-bold text-white">Profit Calculator</h1>
        <Badge className="bg-emerald-500/20 text-emerald-400 border-0 text-xs">Module 17</Badge>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input panel */}
        <div className="bg-[#111218] border border-white/5 rounded-xl p-5">
          <p className="text-sm font-semibold text-white mb-5">Product Details</p>
          <div className="grid grid-cols-2 gap-4 mb-5">
            {field("product_cost", "Product Cost", "number", "$")}
            {field("selling_price", "Selling Price", "number", "$")}
            {field("shipping_cost", "Shipping to Warehouse", "number", "$")}
            {field("ad_spend_daily", "Daily Ad Spend", "number", "$")}
            {field("monthly_units", "Monthly Units Sold")}
          </div>

          <div className="mb-5">
            <label className="text-[10px] font-semibold uppercase text-white/30 block mb-2">Marketplace</label>
            <div className="grid grid-cols-3 gap-2">
              {MARKETPLACES.map((mp) => (
                <button key={mp} onClick={() => setForm(p => ({ ...p, marketplace: mp }))}
                  className={cn("py-2 rounded-lg text-xs font-medium border capitalize transition-all",
                    form.marketplace === mp ? "bg-emerald-500/20 border-emerald-500/40 text-emerald-300" : "bg-white/3 border-white/8 text-white/40 hover:text-white")}>
                  {mp}
                </button>
              ))}
            </div>
          </div>

          <div className="flex gap-3">
            <Button onClick={() => calcMutation.mutate()} disabled={calcMutation.isPending}
              className="flex-1 bg-emerald-600 hover:bg-emerald-500">
              Calculate
            </Button>
            <Button onClick={() => { setCompareAll(true); compareMutation.mutate(); }}
              disabled={compareMutation.isPending} variant="outline"
              className="flex-1 border-white/10 bg-white/5 text-white/60 hover:text-white">
              Compare All Platforms
            </Button>
          </div>
        </div>

        {/* Results panel */}
        <div className="space-y-4">
          {result && (
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
              className="bg-[#111218] border border-white/5 rounded-xl p-5">
              <div className="flex items-center justify-between mb-4">
                <p className="text-sm font-semibold text-white capitalize">{result.marketplace} Profit Analysis</p>
                <span className={cn("text-lg font-bold", result.net_profit_per_unit > 0 ? "text-emerald-400" : "text-red-400")}>
                  {formatCurrency(result.net_profit_per_unit)}/unit
                </span>
              </div>
              <div className="grid grid-cols-2 gap-3 mb-4">
                {[
                  { label: "ROI", value: `${result.roi_percent}%`, color: result.roi_percent > 50 ? "text-emerald-400" : "text-amber-400" },
                  { label: "Margin", value: `${result.margin_percent}%`, color: result.margin_percent > 20 ? "text-emerald-400" : "text-amber-400" },
                  { label: "Monthly Profit", value: formatCurrency(result.net_profit_monthly), color: "text-white" },
                  { label: "Annual Projection", value: formatCurrency(result.annual_net_profit_projection), color: "text-violet-400" },
                  { label: "Break-even Units", value: result.break_even_units_monthly, color: "text-white" },
                  { label: "Total Fees/unit", value: formatCurrency(result.fees_breakdown?.total_per_unit ?? 0), color: "text-amber-400" },
                ].map((s) => (
                  <div key={s.label} className="bg-white/5 rounded-lg p-3">
                    <p className={cn("text-base font-bold", s.color)}>{s.value}</p>
                    <p className="text-[10px] text-white/35">{s.label}</p>
                  </div>
                ))}
              </div>
              <div className="border-t border-white/5 pt-4">
                <p className="text-[10px] font-semibold uppercase text-white/30 mb-2">Fee Breakdown</p>
                <div className="space-y-1.5">
                  {Object.entries(result.fees_breakdown ?? {}).filter(([k]) => k !== "total_per_unit" && k !== "variable_per_unit" && k !== "monthly_fixed").map(([k, v]) => (
                    <div key={k} className="flex justify-between text-xs">
                      <span className="text-white/40 capitalize">{k.replace(/_/g, " ")}</span>
                      <span className="text-white">{formatCurrency(v as number)}</span>
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>
          )}

          {comparison && compareAll && (
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
              className="bg-[#111218] border border-white/5 rounded-xl overflow-hidden">
              <div className="px-4 py-3 border-b border-white/5">
                <p className="text-sm font-semibold text-white">Platform Comparison</p>
              </div>
              {comparison.map((p: any, i: number) => (
                <div key={i} className={cn("flex items-center justify-between px-4 py-3 border-b border-white/3",
                  i === 0 && "bg-emerald-500/5 border-emerald-500/10")}>
                  <div className="flex items-center gap-2">
                    {i === 0 && <span className="text-emerald-400 text-xs font-bold">BEST</span>}
                    <span className="text-sm text-white capitalize">{p.marketplace}</span>
                  </div>
                  <div className="flex items-center gap-6 text-xs">
                    <span className="text-white/40">Fees: {formatCurrency(p.fees_total)}</span>
                    <span className="text-amber-400">{p.roi_percent}% ROI</span>
                    <span className={cn("font-semibold", p.net_profit_monthly > 0 ? "text-emerald-400" : "text-red-400")}>
                      {formatCurrency(p.net_profit_monthly)}/mo
                    </span>
                  </div>
                </div>
              ))}
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
}
