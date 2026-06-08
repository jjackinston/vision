"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, Sparkles, CheckCircle2, AlertTriangle, XCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useMutation } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";

export function SuccessPredictorModal({ open, onClose }: { open: boolean; onClose: () => void }) {
  const [form, setForm] = useState({
    concept: "",
    category: "home",
    cost: 5,
    selling_price: 29.99,
    marketplace: "amazon",
  });
  const [result, setResult] = useState<any>(null);

  const mutation = useMutation({
    mutationFn: () => api.predictSuccess(form),
    onSuccess: setResult,
  });

  const CATEGORIES = ["home", "kitchen", "health_beauty", "sports", "electronics", "clothing", "pets", "toys"];

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            onClick={onClose} className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50" />
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            className="fixed inset-x-4 top-12 bottom-12 max-w-xl mx-auto bg-[#13141A] border border-white/10 rounded-2xl shadow-2xl z-50 flex flex-col overflow-hidden"
          >
            <div className="flex items-center justify-between p-5 border-b border-white/8">
              <div className="flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-violet-400" />
                <h2 className="text-base font-bold text-white">Product Success Predictor</h2>
                <span className="text-xs text-white/30">Module 2</span>
              </div>
              <button onClick={onClose} className="text-white/30 hover:text-white"><X className="w-4 h-4" /></button>
            </div>

            <div className="flex-1 overflow-y-auto p-5">
              {!result ? (
                <>
                  <p className="text-sm text-white/50 mb-6">
                    Predict the probability your product will succeed <em>before</em> you launch.
                    Get success probability, estimated revenue, and risk analysis.
                  </p>

                  <div className="space-y-4">
                    <div>
                      <label className="text-[10px] font-semibold uppercase text-white/30 block mb-1.5">Product Concept</label>
                      <textarea
                        value={form.concept}
                        onChange={(e) => setForm(p => ({ ...p, concept: e.target.value }))}
                        placeholder="Describe your product idea in detail..."
                        rows={3}
                        className="w-full bg-white/5 border border-white/10 rounded-lg p-3 text-sm text-white placeholder:text-white/25 outline-none focus:border-violet-500/50 resize-none"
                      />
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                      {[
                        { key: "cost", label: "Unit Cost", prefix: "$" },
                        { key: "selling_price", label: "Selling Price", prefix: "$" },
                      ].map(({ key, label, prefix }) => (
                        <div key={key}>
                          <label className="text-[10px] font-semibold uppercase text-white/30 block mb-1.5">{label}</label>
                          <div className="relative">
                            <span className="absolute left-3 top-1/2 -translate-y-1/2 text-white/30 text-sm">{prefix}</span>
                            <input type="number" value={(form as any)[key]}
                              onChange={(e) => setForm(p => ({ ...p, [key]: parseFloat(e.target.value) || 0 }))}
                              className="w-full bg-white/5 border border-white/10 rounded-lg pl-7 pr-3 py-2 text-sm text-white outline-none focus:border-violet-500/50"
                            />
                          </div>
                        </div>
                      ))}
                    </div>

                    <div>
                      <label className="text-[10px] font-semibold uppercase text-white/30 block mb-1.5">Category</label>
                      <div className="flex flex-wrap gap-2">
                        {CATEGORIES.map((cat) => (
                          <button key={cat} onClick={() => setForm(p => ({ ...p, category: cat }))}
                            className={cn("px-3 py-1 rounded-full text-xs border capitalize transition-all",
                              form.category === cat
                                ? "bg-violet-500/20 border-violet-500/40 text-violet-300"
                                : "bg-white/3 border-white/8 text-white/40 hover:text-white")}>
                            {cat.replace("_", " ")}
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>

                  <Button onClick={() => mutation.mutate()} disabled={mutation.isPending || !form.concept}
                    className="w-full mt-6 bg-violet-600 hover:bg-violet-500 h-10">
                    {mutation.isPending ? "Analyzing..." : "Predict Success"}
                  </Button>
                </>
              ) : (
                <SuccessResult result={result} onReset={() => setResult(null)} />
              )}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}

function SuccessResult({ result, onReset }: { result: any; onReset: () => void }) {
  const prob = result.success_probability ?? 74;
  const rec = (result.recommendation ?? "launch") as "launch" | "wait" | "avoid";
  const recConfig = ({
    launch: { icon: CheckCircle2, color: "text-emerald-400", bg: "bg-emerald-500/10 border-emerald-500/20", label: "Launch Recommended" },
    wait: { icon: AlertTriangle, color: "text-amber-400", bg: "bg-amber-500/10 border-amber-500/20", label: "Wait for Better Timing" },
    avoid: { icon: XCircle, color: "text-red-400", bg: "bg-red-500/10 border-red-500/20", label: "Avoid This Product" },
  } as const)[rec] ?? { icon: CheckCircle2, color: "text-emerald-400", bg: "bg-emerald-500/10", label: "Launch Recommended" };
  const Icon = recConfig.icon;

  return (
    <div className="space-y-5">
      {/* Probability dial */}
      <div className="text-center py-4">
        <div className={cn("text-6xl font-black mb-2", prob >= 65 ? "text-emerald-400" : prob >= 45 ? "text-amber-400" : "text-red-400")}>
          {prob}%
        </div>
        <p className="text-sm text-white/50">Success Probability</p>
      </div>

      {/* Recommendation banner */}
      <div className={cn("flex items-center gap-3 p-4 rounded-xl border", recConfig.bg)}>
        <Icon className={cn("w-5 h-5 flex-shrink-0", recConfig.color)} />
        <div>
          <p className={cn("text-sm font-semibold", recConfig.color)}>{recConfig.label}</p>
          <p className="text-xs text-white/50">{result.explainable_reasoning?.slice(0, 120) ?? "Based on market analysis"}</p>
        </div>
      </div>

      {/* Financials */}
      <div className="grid grid-cols-3 gap-3">
        {[
          { label: "Est. Monthly Revenue", value: `$${(result.estimated_revenue_monthly ?? 8500).toLocaleString()}` },
          { label: "Est. Monthly Profit", value: `$${(result.estimated_profit_monthly ?? 2100).toLocaleString()}` },
          { label: "Break Even", value: `Month ${result.break_even_months ?? 3}` },
        ].map((s) => (
          <div key={s.label} className="bg-white/5 rounded-lg p-3 text-center">
            <p className="text-sm font-bold text-white">{s.value}</p>
            <p className="text-[9px] text-white/35">{s.label}</p>
          </div>
        ))}
      </div>

      {/* Risk factors */}
      {result.risk_factors?.length > 0 && (
        <div>
          <p className="text-[10px] font-semibold uppercase text-white/30 mb-2">Risk Factors</p>
          <div className="space-y-1.5">
            {result.risk_factors.slice(0, 4).map((r: string, i: number) => (
              <div key={i} className="flex items-start gap-2 text-xs text-white/50">
                <AlertTriangle className="w-3 h-3 text-amber-400 flex-shrink-0 mt-0.5" />
                {r}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Opportunities */}
      {result.opportunities?.length > 0 && (
        <div>
          <p className="text-[10px] font-semibold uppercase text-white/30 mb-2">Opportunities</p>
          <div className="space-y-1.5">
            {result.opportunities.slice(0, 3).map((o: string, i: number) => (
              <div key={i} className="flex items-start gap-2 text-xs text-white/50">
                <CheckCircle2 className="w-3 h-3 text-emerald-400 flex-shrink-0 mt-0.5" />
                {o}
              </div>
            ))}
          </div>
        </div>
      )}

      <Button onClick={onReset} variant="outline" className="w-full border-white/10 bg-white/5 text-white/50 hover:text-white">
        Analyze Another Product
      </Button>
    </div>
  );
}
