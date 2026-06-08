"use client";

import { motion } from "framer-motion";
import { Package, DollarSign, Target, Globe, FileText, Warehouse, CheckCircle2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { useState } from "react";

interface Action {
  priority: "critical" | "high" | "medium" | "low";
  action: string;
  detail: string;
  impact: string;
  icon: string;
}

const iconMap: Record<string, React.ElementType> = {
  package: Package, dollar: DollarSign, target: Target,
  globe: Globe, file: FileText, warehouse: Warehouse,
};

const priorityConfig = {
  critical: { label: "Critical", classes: "bg-red-500/20 text-red-400 border-red-500/30" },
  high: { label: "High", classes: "bg-amber-500/20 text-amber-400 border-amber-500/30" },
  medium: { label: "Medium", classes: "bg-blue-500/20 text-blue-400 border-blue-500/30" },
  low: { label: "Low", classes: "bg-white/10 text-white/40 border-white/10" },
};

export function ActionCard({ action, index }: { action: Action; index: number }) {
  const [done, setDone] = useState(false);
  const Icon = iconMap[action.icon] || Package;
  const pConfig = priorityConfig[action.priority];

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      className={cn(
        "border rounded-lg p-4 transition-all duration-200",
        done
          ? "border-white/5 bg-white/2 opacity-50"
          : "border-white/8 bg-white/3 hover:border-white/15 hover:bg-white/5"
      )}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="w-7 h-7 rounded-md bg-white/5 flex items-center justify-center flex-shrink-0 mt-0.5">
          <Icon className="w-3.5 h-3.5 text-white/50" />
        </div>
        <button
          onClick={() => setDone(!done)}
          className="flex-shrink-0 mt-0.5"
        >
          <CheckCircle2 className={cn(
            "w-4 h-4 transition-colors",
            done ? "text-emerald-400" : "text-white/15 hover:text-white/40"
          )} />
        </button>
      </div>
      <div className="mt-3">
        <div className={cn("inline-flex items-center text-[9px] font-semibold uppercase tracking-wide border rounded px-1.5 py-0.5 mb-2", pConfig.classes)}>
          {pConfig.label}
        </div>
        <p className={cn("text-sm font-medium leading-snug", done ? "line-through text-white/30" : "text-white")}>
          {action.action}
        </p>
        <p className="text-xs text-white/35 mt-1 leading-relaxed">{action.detail}</p>
        <p className="text-xs text-emerald-400/80 mt-2 font-medium">{action.impact}</p>
      </div>
    </motion.div>
  );
}
