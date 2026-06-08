"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, Zap, TrendingUp, DollarSign, Package, BarChart3 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useDigitalTwin } from "@/hooks/useDigitalTwin";
import { useMutation } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { formatCurrency } from "@/lib/utils";
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

interface LaunchSimulatorModalProps {
  open: boolean;
  onClose: () => void;
}

export function LaunchSimulatorModal({ open, onClose }: LaunchSimulatorModalProps) {
  const [form, setForm] = useState({
    product_cost: 5,
    inventory_quantity: 500,
    ppc_budget_daily: 50,
    selling_price: 29.99,
    marketplace: "amazon",
  });
  const [result, setResult] = useState<any>(null);

  const mutation = useMutation({
    mutationFn: () => api.simulateLaunch(form),
    onSuccess: (data) => setResult(data),
  });

  const field = (key: keyof typeof form, label: string, prefix = "") => (
    <div>
      <label className="text-[10px] font-semibold uppercase text-white/30 block mb-1.5">{label}</label>
      <div className="relative">
        {prefix && <span className="absolute left-3 top-1/2 -translate-y-1/2 text-white/30 text-sm">{prefix}</span>}
        <input
          type="number"
          value={form[key]}
          onChange={(e) => setForm(prev => ({ ...prev, [key]: parseFloat(e.target.value) || 0 }))}
          className={`w-full bg-white/5 border border-white/10 rounded-lg py-2 text-sm text-white outline-none focus:border-violet-500/50 ${prefix ? "pl-7 pr-3" : "px-3"}`}
        />
      </div>
    </div>
  );

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            onClick={onClose} className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50" />
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="fixed inset-x-4 top-8 bottom-8 max-w-3xl mx-auto bg-[#13141A] border border-white/10 rounded-2xl shadow-2xl z-50 flex flex-col overflow-hidden"
          >
            {/* Header */}
            <div className="flex items-center justify-between p-5 border-b border-white/8">
              <div className="flex items-center gap-2">
                <Zap className="w-5 h-5 text-amber-400" />
                <h2 className="text-base font-bold text-white">Product Launch Simulator</h2>
                <span className="text-xs text-white/30">Module 10</span>
              </div>
              <button onClick={onClose} className="text-white/30 hover:text-white">
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-5">
              {!result ? (
                <div>
                  <p className="text-sm text-white/50 mb-6">
                    Simulate your product launch before spending a dollar. Get projected revenue,
                    cash flow, and ROI across 3 scenarios.
                  </p>
                  <div className="grid grid-cols-2 gap-4 mb-6">
                    {field("product_cost", "Product Cost (per unit)", "$")}
                    {field("selling_price", "Selling Price", "$")}
                    {field("inventory_quantity", "Initial Inventory (units)")}
                    {field("ppc_budget_daily", "Daily PPC Budget", "$")}
                  </div>
                  <div className="mb-6">
                    <label className="text-[10px] font-semibold uppercase text-white/30 block mb-1.5">Marketplace</label>
                    <div className="flex gap-2">
                      {["amazon", "walmart", "shopify"].map((mp) => (
                        <button key={mp} onClick={() => setForm(p => ({ ...p, marketplace: mp }))}
                          className={`px-4 py-1.5 rounded-lg text-xs font-medium border transition-all capitalize ${form.marketplace === mp ? "bg-violet-500/20 border-violet-500/40 text-violet-300" : "bg-white/3 border-white/10 text-white/40 hover:text-white"}`}>
                          {mp}
                        </button>
                      ))}
                    </div>
                  </div>
                  <Button onClick={() => mutation.mutate()} disabled={mutation.isPending}
                    className="w-full bg-amber-500 hover:bg-amber-400 text-black font-semibold h-10">
                    {mutation.isPending ? "Simulating..." : "Run Launch Simulation"}
                  </Button>
                </div>
              ) : (
                <LaunchResults result={result} form={form} onReset={() => setResult(null)} />
              )}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}

function LaunchResults({ result, form, onReset }: any) {
  const [activeScenario, setActiveScenario] = useState("realistic");
  const scenarios = result?.scenarios || {
    conservative: { roi_percent: 180, profit_6m: 8200 },
    realistic: { roi_percent: 340, profit_6m: 16400 },
    optimistic: { roi_percent: 580, profit_6m: 28900 },
  };

  const chartData = Array.from({ length: 6 }, (_, i) => ({
    month: `M${i + 1}`,
    conservative: Math.round((scenarios.conservative?.monthly_cash_flow?.[i] ?? (i + 1) * 800)),
    realistic: Math.round((scenarios.realistic?.monthly_cash_flow?.[i] ?? (i + 1) * 1600)),
    optimistic: Math.round((scenarios.optimistic?.monthly_cash_flow?.[i] ?? (i + 1) * 2800)),
  }));

  return (
    <div>
      <div className="flex gap-2 mb-5">
        {["conservative", "realistic", "optimistic"].map((s) => (
          <button key={s} onClick={() => setActiveScenario(s)}
            className={`flex-1 py-2 rounded-lg text-xs font-semibold border capitalize transition-all ${activeScenario === s ? "bg-violet-500/20 border-violet-500/40 text-violet-300" : "bg-white/3 border-white/8 text-white/40 hover:text-white"}`}>
            {s}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-3 gap-3 mb-5">
        {[
          { label: "6-Month Profit", value: formatCurrency(scenarios[activeScenario]?.profit_6m ?? 16400) },
          { label: "ROI", value: `${scenarios[activeScenario]?.roi_percent ?? 340}%` },
          { label: "Break Even", value: scenarios[activeScenario]?.break_even_date ?? "Month 2" },
        ].map((stat) => (
          <div key={stat.label} className="bg-white/5 rounded-lg p-3 text-center">
            <p className="text-lg font-bold text-white">{stat.value}</p>
            <p className="text-[10px] text-white/40">{stat.label}</p>
          </div>
        ))}
      </div>

      <div className="bg-white/3 rounded-xl p-4 mb-4">
        <p className="text-xs text-white/30 mb-3">Cash Flow Projection (6 months)</p>
        <ResponsiveContainer width="100%" height={160}>
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="real" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#8B5CF6" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#8B5CF6" stopOpacity={0} />
              </linearGradient>
            </defs>
            <XAxis dataKey="month" tick={{ fontSize: 10, fill: "rgba(255,255,255,0.3)" }} tickLine={false} axisLine={false} />
            <YAxis tick={{ fontSize: 10, fill: "rgba(255,255,255,0.3)" }} tickLine={false} axisLine={false} tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`} />
            <Tooltip contentStyle={{ background: "#1A1B22", border: "1px solid rgba(255,255,255,0.1)", borderRadius: "8px" }} formatter={(v: number) => [`$${v.toLocaleString()}`, "Cash Flow"]} />
            <Area type="monotone" dataKey={activeScenario} stroke="#8B5CF6" strokeWidth={2} fill="url(#real)" />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {result?.key_assumptions && (
        <div className="bg-white/3 rounded-xl p-4 mb-4">
          <p className="text-[10px] font-semibold uppercase text-white/30 mb-2">Key Assumptions</p>
          <ul className="space-y-1">
            {result.key_assumptions.slice(0, 4).map((a: string, i: number) => (
              <li key={i} className="text-xs text-white/50 flex items-start gap-2">
                <span className="text-violet-400 mt-0.5">•</span> {a}
              </li>
            ))}
          </ul>
        </div>
      )}

      <Button onClick={onReset} variant="outline" className="w-full border-white/10 bg-white/5 text-white/50 hover:text-white">
        Run Another Simulation
      </Button>
    </div>
  );
}
