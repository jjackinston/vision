"use client";

import { motion } from "framer-motion";
import { TrendingUp, TrendingDown } from "lucide-react";
import { cn } from "@/lib/utils";

interface AIScoreCardProps {
  title: string;
  score: number;
  trend: number;
  description: string;
  color: "emerald" | "violet" | "amber" | "red";
  invertScore?: boolean;
}

export function AIScoreCard({ title, score, trend, description, color, invertScore }: AIScoreCardProps) {
  const isGood = invertScore ? score < 40 : score >= 70;
  const isWarn = invertScore ? score >= 40 && score < 70 : score >= 40 && score < 70;

  const scoreColor = isGood ? "text-emerald-400" : isWarn ? "text-amber-400" : "text-red-400";
  const barColor = isGood ? "bg-emerald-500" : isWarn ? "bg-amber-500" : "bg-red-500";

  return (
    <div className="bg-[#111218] border border-white/5 rounded-xl p-4">
      <div className="flex items-center justify-between mb-3">
        <p className="text-xs font-semibold text-white/60">{title}</p>
        <div className={cn(
          "flex items-center gap-1 text-xs",
          trend >= 0 ? "text-emerald-400" : "text-red-400"
        )}>
          {trend >= 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
          {trend >= 0 ? "+" : ""}{trend}
        </div>
      </div>
      <div className="flex items-end gap-3 mb-3">
        <span className={cn("text-3xl font-bold", scoreColor)}>{score}</span>
        <span className="text-white/20 text-sm mb-1">/100</span>
      </div>
      <div className="w-full bg-white/5 rounded-full h-1.5 mb-3">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${score}%` }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className={cn("h-1.5 rounded-full", barColor)}
        />
      </div>
      <p className="text-xs text-white/30 leading-relaxed">{description}</p>
    </div>
  );
}
