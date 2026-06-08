"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

interface ScoreMeterProps {
  label: string;
  score: number;
  size?: "sm" | "md" | "lg";
  invert?: boolean;
}

export function ScoreMeter({ label, score, size = "md", invert = false }: ScoreMeterProps) {
  const isGood = invert ? score < 35 : score >= 65;
  const isWarn = invert
    ? score >= 35 && score < 60
    : score >= 40 && score < 65;

  const color = isGood ? "#10B981" : isWarn ? "#F59E0B" : "#EF4444";
  const bgColor = isGood ? "bg-emerald-500" : isWarn ? "bg-amber-500" : "bg-red-500";

  const sizes = {
    sm: { ring: "w-12 h-12", text: "text-sm", label: "text-[9px]", stroke: 3, r: 18 },
    md: { ring: "w-16 h-16", text: "text-base", label: "text-[10px]", stroke: 3.5, r: 24 },
    lg: { ring: "w-20 h-20", text: "text-xl", label: "text-xs", stroke: 4, r: 30 },
  };
  const s = sizes[size];
  const circumference = 2 * Math.PI * s.r;
  const offset = circumference - (score / 100) * circumference;

  return (
    <div className="flex flex-col items-center gap-1">
      <div className={cn("relative", s.ring)}>
        <svg className="w-full h-full -rotate-90" viewBox={`0 0 ${s.r * 2 + 8} ${s.r * 2 + 8}`}>
          <circle cx={s.r + 4} cy={s.r + 4} r={s.r} fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth={s.stroke} />
          <motion.circle
            cx={s.r + 4} cy={s.r + 4} r={s.r} fill="none"
            stroke={color} strokeWidth={s.stroke}
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: offset }}
            transition={{ duration: 0.8, ease: "easeOut", delay: 0.1 }}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className={cn("font-bold text-white", s.text)}>{score}</span>
        </div>
      </div>
      <span className={cn("text-white/40 font-medium", s.label)}>{label}</span>
    </div>
  );
}
