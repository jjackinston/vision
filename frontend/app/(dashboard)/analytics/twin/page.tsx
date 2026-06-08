"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Globe, Zap, TrendingUp, DollarSign, CheckCircle2, XCircle, AlertTriangle } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useDigitalTwin } from "@/hooks/useDigitalTwin";
import { cn, formatCurrency } from "@/lib/utils";
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";

const SCENARIOS = [
  { id: "price_change", label: "Price Change", icon: DollarSign, description: "What if I change my price by X%?" },
  { id: "ppc_increase", label: "Increase PPC", icon: TrendingUp, description: "What if I double my ad budget?" },
  { id: "new_product", label: "Launch Product", icon: Zap, description: "What if I launch a new product?" },
  { id: "inventory_change", label: "Inventory Change", icon: Globe, description: "What if I order more inventory?" },
];

export default function DigitalTwinPage() {
  const [scenario, setScenario] = useState("price_change");
  const [params, setParams] = useState<Record<string, any>>({ change_percent: 10 });
  const [months, setMonths] = useState(6);
  const { simulate, result, isSimulating, reset } = useDigitalTwin();

  const simData = (result as any)?.simulation;

  const chartData = simData?.months?.map((m: any, i: number) => ({
    month: `Month ${m.month ?? i + 1}`,
    revenue: m.revenue,
    profit: m.profit,
    cash_flow: m.cash_flow,
  })) ?? Array.from({ length: months }, (_, i) => ({
    month: `Month ${i + 1}`,
    revenue: 16000 * (1 + (i * 0.08)),
    profit: 4200 * (1 + (i * 0.10)),
    cash_flow: 3800 * (1 + (i * 0.09)),
  }));

  return (
    <div className="p-6 max-w-[1400px] mx-auto">
      <div className="flex items-center gap-2 mb-6">
        <Globe className="w-5 h-5 text-blue-400" />
        <h1 className="text-xl font-bold text-white">Digital Twin</h1>
        <Badge className="bg-blue-500/20 text-blue-400 border-0 text-xs">Module 19 — Beta</Badge>
      </div>
      <p className="text-sm text-white/40 mb-6">
        Simulate your business decisions before executing them. See projected outcomes for any what-if scenario.
      </p>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Config panel */}
        <div className="bg-[#111218] border border-white/5 rounded-xl p-5">
          <p className="text-sm font-semibold text-white mb-4">Scenario Configuration</p>
          <div className="grid grid-cols-2 gap-2 mb-5">
            {SCENARIOS.map((s) => {
              const Icon = s.icon;
              return (
                <button key={s.id} onClick={() => setScenario(s.id)}
                  className={cn("p-3 rounded-xl border text-left transition-all",
                    scenario === s.id ? "bg-blue-500/15 border-blue-500/30" : "bg-white/3 border-white/8 hover:border-white/20")}>
                  <Icon className={cn("w-4 h-4 mb-2", scenario === s.id ? "text-blue-400" : "text-white/30")} />
                  <p className={cn("text-xs font-semibold", scenario === s.id ? "text-blue-300" : "text-white/60")}>{s.label}</p>
                </button>
              );
            })}
          </div>

          {/* Scenario params */}
          <div className="space-y-3 mb-5">
            {scenario === "price_change" && (
              <div>
                <label className="text-[10px] uppercase text-white/30 font-semibold block mb-1.5">Price Change %</label>
                <input type="number" value={params.change_percent ?? 10}
                  onChange={(e) => setParams({ change_percent: parseFloat(e.target.value) })}
                  className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white outline-none focus:border-blue-500/50" />
              </div>
            )}
            {scenario === "ppc_increase" && (
              <div>
                <label className="text-[10px] uppercase text-white/30 font-semibold block mb-1.5">Daily Budget Increase ($)</label>
                <input type="number" value={params.increase_amount ?? 50}
                  onChange={(e) => setParams({ increase_amount: parseFloat(e.target.value) })}
                  className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white outline-none" />
              </div>
            )}
            {scenario === "new_product" && (
              <>
                <div>
                  <label className="text-[10px] uppercase text-white/30 font-semibold block mb-1.5">Product Name</label>
                  <input type="text" placeholder="New product name"
                    onChange={(e) => setParams(p => ({ ...p, product_name: e.target.value }))}
                    className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white outline-none" />
                </div>
                <div>
                  <label className="text-[10px] uppercase text-white/30 font-semibold block mb-1.5">Selling Price ($)</label>
                  <input type="number" value={params.price ?? 29.99}
                    onChange={(e) => setParams(p => ({ ...p, price: parseFloat(e.target.value) }))}
                    className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white outline-none" />
                </div>
              </>
            )}
            <div>
              <label className="text-[10px] uppercase text-white/30 font-semibold block mb-1.5">Forecast Months</label>
              <div className="flex gap-2">
                {[3, 6, 12].map((m) => (
                  <button key={m} onClick={() => setMonths(m)}
                    className={cn("flex-1 py-1.5 rounded-lg text-xs border transition-all",
                      months === m ? "bg-blue-500/20 border-blue-500/40 text-blue-300" : "bg-white/3 border-white/8 text-white/40 hover:text-white")}>
                    {m}mo
                  </button>
                ))}
              </div>
            </div>
          </div>

          <Button onClick={() => simulate({ scenario_type: scenario as any, parameters: params, forecast_months: months })}
            disabled={isSimulating} className="w-full bg-blue-600 hover:bg-blue-500">
            {isSimulating ? "Simulating..." : "Run Simulation"}
          </Button>
        </div>

        {/* Results */}
        <div className="lg:col-span-2 space-y-4">
          {simData && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
              className={cn("border rounded-xl p-4 flex items-center gap-4",
                simData.recommendation === "go" ? "bg-emerald-500/8 border-emerald-500/20" :
                simData.recommendation === "pause" ? "bg-amber-500/8 border-amber-500/20" :
                "bg-red-500/8 border-red-500/20")}>
              {simData.recommendation === "go"
                ? <CheckCircle2 className="w-6 h-6 text-emerald-400" />
                : simData.recommendation === "pause"
                ? <AlertTriangle className="w-6 h-6 text-amber-400" />
                : <XCircle className="w-6 h-6 text-red-400" />
              }
              <div>
                <p className={cn("font-semibold capitalize",
                  simData.recommendation === "go" ? "text-emerald-400" : simData.recommendation === "pause" ? "text-amber-400" : "text-red-400")}>
                  Recommendation: {simData.recommendation === "go" ? "Proceed" : simData.recommendation === "pause" ? "Wait & Monitor" : "Do Not Proceed"}
                </p>
                <p className="text-xs text-white/50">{simData.scenario_summary}</p>
              </div>
            </motion.div>
          )}

          {/* KPI projections */}
          {simData && (
            <div className="grid grid-cols-3 gap-3">
              {[
                { label: `${months}M Revenue`, value: formatCurrency(simData.total_6m_revenue ?? chartData.reduce((s: number, d: any) => s + d.revenue, 0)) },
                { label: `${months}M Profit`, value: formatCurrency(simData.total_6m_profit ?? chartData.reduce((s: number, d: any) => s + d.profit, 0)) },
                { label: "ROI", value: `${simData.roi_percent ?? 0}%` },
              ].map((s) => (
                <div key={s.label} className="bg-[#111218] border border-white/5 rounded-xl p-4 text-center">
                  <p className="text-xl font-bold text-white">{s.value}</p>
                  <p className="text-xs text-white/40">{s.label}</p>
                </div>
              ))}
            </div>
          )}

          {/* Chart */}
          <div className="bg-[#111218] border border-white/5 rounded-xl p-5">
            <p className="text-sm font-semibold text-white mb-4">Projected Revenue & Profit</p>
            <ResponsiveContainer width="100%" height={240}>
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="rev" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#3B82F6" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="prof" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10B981" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#10B981" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                <XAxis dataKey="month" tick={{ fontSize: 10, fill: "rgba(255,255,255,0.3)" }} tickLine={false} axisLine={false} />
                <YAxis tick={{ fontSize: 10, fill: "rgba(255,255,255,0.3)" }} tickLine={false} axisLine={false} tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`} />
                <Tooltip contentStyle={{ background: "#1A1B22", border: "1px solid rgba(255,255,255,0.1)", borderRadius: "8px" }}
                  formatter={(v: number, name: string) => [formatCurrency(v), name.replace("_", " ")]} />
                <Area type="monotone" dataKey="revenue" stroke="#3B82F6" strokeWidth={2} fill="url(#rev)" name="revenue" />
                <Area type="monotone" dataKey="profit" stroke="#10B981" strokeWidth={2} fill="url(#prof)" name="profit" />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          {/* Key assumptions */}
          {simData?.key_assumptions && (
            <div className="bg-[#111218] border border-white/5 rounded-xl p-4">
              <p className="text-[10px] font-semibold uppercase text-white/30 mb-2">Key Assumptions</p>
              <ul className="space-y-1">
                {simData.key_assumptions.map((a: string, i: number) => (
                  <li key={i} className="text-xs text-white/50 flex items-start gap-2">
                    <span className="text-blue-400">•</span> {a}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
