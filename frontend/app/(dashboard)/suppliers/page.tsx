"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Warehouse, Shield, AlertTriangle, MessageSquare, TrendingDown, Star, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useMutation, useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { toast } from "sonner";
import { cn, formatNumber } from "@/lib/utils";

export default function SuppliersPage() {
  const [tab, setTab] = useState<"analyze" | "negotiate" | "tracked">("analyze");
  const [supplierName, setSupplierName] = useState("");
  const [country, setCountry] = useState("CN");
  const [result, setResult] = useState<any>(null);
  const [negotiationForm, setNegForm] = useState({ goal: "price_reduction", current_price: 5.0, target_price: 3.80, current_moq: 1000, target_moq: 500 });
  const [negotiationScript, setNegotiationScript] = useState<any>(null);

  const analyzeMutation = useMutation({
    mutationFn: () => api.analyzeSupplierByName(supplierName, country),
    onSuccess: (data) => {
      setResult(data);
      toast.success("Supplier analysis complete");
    },
    onError: () => toast.error("Supplier analysis failed — check the name and try again"),
  });

  const negotiateMutation = useMutation({
    mutationFn: () => api.negotiateSupplier(result?.supplier_id || "00000000-0000-0000-0000-000000000000", negotiationForm),
    onSuccess: (data) => {
      setNegotiationScript(data);
      toast.success("Negotiation script ready");
    },
    onError: () => toast.error("Script generation failed — try again"),
  });

  const COUNTRIES = [{ code: "CN", label: "China" }, { code: "VN", label: "Vietnam" }, { code: "IN", label: "India" }, { code: "TR", label: "Turkey" }, { code: "MX", label: "Mexico" }, { code: "US", label: "USA" }];

  return (
    <div className="p-6 max-w-[1400px] mx-auto">
      <div className="flex items-center gap-2 mb-6">
        <Warehouse className="w-5 h-5 text-emerald-400" />
        <h1 className="text-xl font-bold text-white">Supplier Intelligence</h1>
        <Badge className="bg-emerald-500/20 text-emerald-400 border-0 text-xs">Modules 12 + 13</Badge>
      </div>

      <div className="flex gap-1 mb-6 bg-white/5 rounded-lg p-1 w-fit">
        {[{ id: "analyze", label: "Analyze Supplier" }, { id: "negotiate", label: "AI Negotiation" }, { id: "tracked", label: "My Suppliers" }]
          .map((t) => (
            <button key={t.id} onClick={() => setTab(t.id as any)}
              className={cn("px-4 py-1.5 rounded-md text-xs font-medium transition-all",
                tab === t.id ? "bg-emerald-600 text-white" : "text-white/40 hover:text-white")}>
              {t.label}
            </button>
          ))}
      </div>

      {tab === "analyze" && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-[#111218] border border-white/5 rounded-xl p-5">
            <p className="text-sm font-semibold text-white mb-4">Analyze a Supplier</p>
            <div className="space-y-3 mb-4">
              <div>
                <label className="text-[10px] uppercase text-white/30 font-semibold block mb-1.5">Supplier Name</label>
                <input value={supplierName} onChange={(e) => setSupplierName(e.target.value)}
                  placeholder="Shenzhen EcoPack Trading Co. Ltd"
                  className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2.5 text-sm text-white placeholder:text-white/20 outline-none focus:border-emerald-500/50" />
              </div>
              <div>
                <label className="text-[10px] uppercase text-white/30 font-semibold block mb-2">Country</label>
                <div className="flex flex-wrap gap-2">
                  {COUNTRIES.map((c) => (
                    <button key={c.code} onClick={() => setCountry(c.code)}
                      className={cn("px-3 py-1.5 rounded-lg text-xs border transition-all",
                        country === c.code ? "bg-emerald-500/20 border-emerald-500/40 text-emerald-300" : "bg-white/3 border-white/8 text-white/40 hover:text-white")}>
                      {c.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>
            <Button onClick={() => analyzeMutation.mutate()} disabled={analyzeMutation.isPending || !supplierName}
              className="w-full bg-emerald-600 hover:bg-emerald-500">
              {analyzeMutation.isPending ? <><RefreshCw className="w-4 h-4 animate-spin mr-2" />Analyzing...</> : "Analyze Supplier"}
            </Button>
          </div>

          {result ? <SupplierAnalysisResult data={result} onNegotiate={() => setTab("negotiate")} /> : (
            <div className="bg-[#111218] border border-white/5 border-dashed rounded-xl p-12 text-center">
              <Warehouse className="w-10 h-10 text-white/10 mx-auto mb-3" />
              <p className="text-white/30 text-sm">Enter supplier name to get AI-powered analysis</p>
            </div>
          )}
        </div>
      )}

      {tab === "negotiate" && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-[#111218] border border-white/5 rounded-xl p-5">
            <p className="text-sm font-semibold text-white mb-2">AI Negotiation Assistant</p>
            <p className="text-xs text-white/40 mb-5">Get a complete negotiation script and strategy</p>
            <div className="space-y-3 mb-4">
              {[
                { key: "current_price", label: "Current Unit Price ($)" },
                { key: "target_price", label: "Target Price ($)" },
                { key: "current_moq", label: "Current MOQ (units)" },
                { key: "target_moq", label: "Target MOQ (units)" },
              ].map(({ key, label }) => (
                <div key={key}>
                  <label className="text-[10px] uppercase text-white/30 font-semibold block mb-1.5">{label}</label>
                  <input type="number" value={(negotiationForm as any)[key]}
                    onChange={(e) => setNegForm(p => ({ ...p, [key]: parseFloat(e.target.value) || 0 }))}
                    className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white outline-none focus:border-emerald-500/50" />
                </div>
              ))}
            </div>
            <Button onClick={() => negotiateMutation.mutate()} disabled={negotiateMutation.isPending}
              className="w-full bg-emerald-600 hover:bg-emerald-500">
              {negotiateMutation.isPending ? "Generating..." : "Generate Negotiation Script"}
            </Button>
          </div>

          {negotiationScript ? <NegotiationResult data={negotiationScript} /> : (
            <div className="bg-[#111218] border border-white/5 border-dashed rounded-xl p-12 text-center">
              <MessageSquare className="w-10 h-10 text-white/10 mx-auto mb-3" />
              <p className="text-white/30 text-sm">Your AI negotiation strategy appears here</p>
            </div>
          )}
        </div>
      )}

      {tab === "tracked" && <TrackedSuppliers />}
    </div>
  );
}

function SupplierAnalysisResult({ data, onNegotiate }: { data: any; onNegotiate: () => void }) {
  const scores = [
    { label: "Trust", score: data.trust_score ?? 72, color: "emerald" },
    { label: "Quality", score: data.quality_score ?? 68, color: "blue" },
    { label: "Reliability", score: data.reliability_score ?? 75, color: "violet" },
    { label: "Risk", score: data.risk_score ?? 35, color: "red", invert: true },
  ];
  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
      <div className="bg-[#111218] border border-white/5 rounded-xl p-5">
        <p className="text-sm font-semibold text-white mb-4">Supplier Intelligence Report</p>
        <div className="grid grid-cols-4 gap-3 mb-4">
          {scores.map((s) => {
            const colorMap: Record<string, string> = { emerald: "text-emerald-400", blue: "text-blue-400", violet: "text-violet-400", red: "text-red-400" };
            const isGood = s.invert ? s.score < 40 : s.score >= 60;
            return (
              <div key={s.label} className="text-center">
                <p className={cn("text-2xl font-bold", colorMap[s.color])}>{s.score}</p>
                <p className="text-[10px] text-white/40">{s.label}</p>
              </div>
            );
          })}
        </div>
        <div className="grid grid-cols-2 gap-3 text-xs border-t border-white/5 pt-4">
          {[
            { label: "Lead Time", value: `${data.avg_lead_time_days ?? 35} days` },
            { label: "Min Order", value: formatNumber(data.min_order_qty ?? 500) + " units" },
            { label: "Payment", value: data.payment_terms ?? "30% deposit, 70% before ship" },
            { label: "Country", value: data.country ?? "CN" },
          ].map((item) => (
            <div key={item.label}>
              <p className="text-white/30">{item.label}</p>
              <p className="text-white font-medium">{item.value}</p>
            </div>
          ))}
        </div>
      </div>
      {data.risk_factors?.length > 0 && (
        <div className="bg-red-500/5 border border-red-500/15 rounded-xl p-4">
          <p className="text-xs font-semibold uppercase text-red-400 mb-2">Risk Factors</p>
          {data.risk_factors.slice(0, 3).map((r: string, i: number) => (
            <p key={i} className="text-xs text-white/50 flex gap-2"><AlertTriangle className="w-3 h-3 text-red-400 flex-shrink-0 mt-0.5" />{r}</p>
          ))}
        </div>
      )}
      <Button onClick={onNegotiate} className="w-full bg-violet-600 hover:bg-violet-500">
        <MessageSquare className="w-3.5 h-3.5 mr-2" />Generate Negotiation Strategy
      </Button>
    </motion.div>
  );
}

function NegotiationResult({ data }: { data: any }) {
  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
      <div className="bg-[#111218] border border-white/5 rounded-xl p-4">
        <p className="text-xs font-semibold uppercase text-white/30 mb-2">Success Probability</p>
        <p className="text-3xl font-black text-emerald-400">{data.success_probability ?? 68}%</p>
        <div className="flex gap-4 mt-2 text-xs text-white/40">
          <span>Achievable price: <span className="text-white font-semibold">${data.estimated_achievable_price ?? "4.20"}</span></span>
          <span>Achievable MOQ: <span className="text-white font-semibold">{data.estimated_achievable_moq ?? 600}</span></span>
        </div>
      </div>
      {data.opening_email && (
        <div className="bg-[#111218] border border-white/5 rounded-xl p-4">
          <p className="text-xs font-semibold uppercase text-white/30 mb-2">Opening Email</p>
          <p className="text-xs text-white/60 leading-relaxed max-h-48 overflow-y-auto">{data.opening_email}</p>
        </div>
      )}
      {data.negotiation_script?.length > 0 && (
        <div className="bg-[#111218] border border-white/5 rounded-xl p-4">
          <p className="text-xs font-semibold uppercase text-white/30 mb-3">Negotiation Phases</p>
          <div className="space-y-3">
            {data.negotiation_script.map((phase: any, i: number) => (
              <div key={i} className="border-l-2 border-violet-500/40 pl-3">
                <p className="text-xs font-semibold text-violet-400 capitalize mb-1">{phase.phase}</p>
                <p className="text-xs text-white/60">{phase.script}</p>
                {phase.psychological_principle && (
                  <p className="text-[10px] text-white/25 mt-1">Principle: {phase.psychological_principle}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </motion.div>
  );
}

function TrackedSuppliers() {
  const { data: suppliers, isLoading } = useQuery({
    queryKey: ["suppliers-list"],
    queryFn: () => api.getSuppliers(),
    staleTime: 1000 * 60 * 5,
  });

  const rows: any[] = Array.isArray(suppliers) ? suppliers : [];

  if (isLoading) {
    return <div className="bg-[#111218] border border-white/5 rounded-xl p-8 text-center text-white/30 text-sm">Loading suppliers…</div>;
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
      {rows.map((s: any, i: number) => (
        <div key={i} className="bg-[#111218] border border-white/5 rounded-xl p-4">
          <div className="flex items-center justify-between mb-3">
            <p className="text-sm font-semibold text-white">{s.name}</p>
            <Badge className="bg-white/5 text-white/40 border-0 text-[10px]">{s.country}</Badge>
          </div>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div><p className="text-white/30">Trust</p><p className={cn("font-semibold", (s.trust_score ?? 0) >= 70 ? "text-emerald-400" : "text-amber-400")}>{s.trust_score ?? "–"}/100</p></div>
            <div><p className="text-white/30">Risk</p><p className={cn("font-semibold", (s.risk_score ?? 100) < 40 ? "text-emerald-400" : "text-red-400")}>{s.risk_score ?? "–"}/100</p></div>
            <div><p className="text-white/30">Lead Time</p><p className="text-white font-semibold">{s.avg_lead_time_days ?? "–"}d</p></div>
            <div><p className="text-white/30">MOQ</p><p className="text-white font-semibold">{s.min_order_qty ? formatNumber(s.min_order_qty) : "–"}</p></div>
          </div>
        </div>
      ))}
      {rows.length === 0 && (
        <div className="col-span-3 bg-[#111218] border border-white/5 rounded-xl p-8 text-center text-white/30 text-sm">No tracked suppliers yet</div>
      )}
    </div>
  );
}
