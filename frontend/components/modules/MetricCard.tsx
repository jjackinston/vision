"use client";

import { motion } from "framer-motion";
import { TrendingUp, TrendingDown, LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface MetricCardProps {
  label: string;
  value: string;
  change: number;
  icon: LucideIcon;
  color: "emerald" | "violet" | "blue" | "amber";
}

const colorConfig = {
  emerald: { bg: "bg-emerald-500/10", text: "text-emerald-400", border: "border-emerald-500/20" },
  violet: { bg: "bg-violet-500/10", text: "text-violet-400", border: "border-violet-500/20" },
  blue: { bg: "bg-blue-500/10", text: "text-blue-400", border: "border-blue-500/20" },
  amber: { bg: "bg-amber-500/10", text: "text-amber-400", border: "border-amber-500/20" },
};

export function MetricCard({ label, value, change, icon: Icon, color }: MetricCardProps) {
  const colors = colorConfig[color];
  const isPositive = change >= 0;

  return (
    <motion.div
      whileHover={{ scale: 1.01 }}
      className="bg-[#111218] border border-white/5 rounded-xl p-4 relative overflow-hidden"
    >
      <div className={cn("absolute inset-0 opacity-5", colors.bg)} />
      <div className="relative">
        <div className="flex items-center justify-between mb-3">
          <div className={cn("w-8 h-8 rounded-lg flex items-center justify-center", colors.bg)}>
            <Icon className={cn("w-4 h-4", colors.text)} />
          </div>
          <div className={cn(
            "flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-full",
            isPositive ? "bg-emerald-500/15 text-emerald-400" : "bg-red-500/15 text-red-400"
          )}>
            {isPositive ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
            {isPositive ? "+" : ""}{change}{typeof change === "number" && Math.abs(change) < 10 ? "%" : ""}
          </div>
        </div>
        <p className="text-2xl font-bold text-white mb-1">{value}</p>
        <p className="text-xs text-white/40">{label}</p>
      </div>
    </motion.div>
  );
}
