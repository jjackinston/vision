"use client";

import { motion } from "framer-motion";
import { useState } from "react";
import { Bot, Play, Pause, Activity, Zap } from "lucide-react";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";

const agents = [
  { name: "Product Research Agent", status: "running", lastAction: "Scanning 847 Amazon categories", findings: 12, color: "violet" },
  { name: "Trend Detection Agent", status: "running", lastAction: "Monitoring TikTok & Reddit", findings: 5, color: "blue" },
  { name: "Competitor Agent", status: "running", lastAction: "Analyzing 23 competitor ASINs", findings: 8, color: "amber" },
  { name: "Inventory Agent", status: "alert", lastAction: "⚠ 2 products critical stockout", findings: 2, color: "red" },
  { name: "PPC Optimization Agent", status: "idle", lastAction: "Last run: 2 hours ago", findings: 3, color: "emerald" },
  { name: "Listing Agent", status: "running", lastAction: "Optimizing 7 listings", findings: 7, color: "pink" },
];

const colorMap: Record<string, string> = {
  violet: "text-violet-400 bg-violet-500/15",
  blue: "text-blue-400 bg-blue-500/15",
  amber: "text-amber-400 bg-amber-500/15",
  red: "text-red-400 bg-red-500/15",
  emerald: "text-emerald-400 bg-emerald-500/15",
  pink: "text-pink-400 bg-pink-500/15",
};

export function AgentStatusPanel() {
  const [paused, setPaused] = useState<string[]>([]);

  const toggle = (name: string) =>
    setPaused((p) => p.includes(name) ? p.filter((n) => n !== name) : [...p, name]);

  return (
    <div className="bg-[#111218] border border-white/5 rounded-xl p-5">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Bot className="w-4 h-4 text-violet-400" />
          <h3 className="text-sm font-semibold text-white">AI Agent Fleet</h3>
          <Badge className="bg-emerald-500/20 text-emerald-400 border-0 text-xs">
            <Activity className="w-2.5 h-2.5 mr-1 animate-pulse" />
            Live
          </Badge>
        </div>
        <span className="text-xs text-white/30">5 active / 6 total</span>
      </div>
      <div className="space-y-2">
        {agents.map((agent, i) => {
          const isPaused = paused.includes(agent.name);
          const isAlert = agent.status === "alert";
          return (
            <motion.div
              key={agent.name}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.05 }}
              className="flex items-center gap-3 p-2.5 rounded-lg hover:bg-white/3 transition-colors"
            >
              <div className={cn("w-7 h-7 rounded-md flex items-center justify-center flex-shrink-0", colorMap[agent.color])}>
                <Zap className="w-3.5 h-3.5" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-xs font-medium text-white truncate">{agent.name}</p>
                <p className={cn("text-[10px] truncate mt-0.5", isAlert ? "text-red-400" : "text-white/30")}>
                  {agent.lastAction}
                </p>
              </div>
              <div className="flex items-center gap-2 flex-shrink-0">
                {agent.findings > 0 && (
                  <span className="text-[10px] text-white/40 bg-white/8 px-1.5 py-0.5 rounded">
                    {agent.findings} findings
                  </span>
                )}
                <button
                  onClick={() => toggle(agent.name)}
                  className="w-5 h-5 flex items-center justify-center text-white/20 hover:text-white/60 transition-colors"
                >
                  {isPaused ? <Play className="w-3 h-3" /> : <Pause className="w-3 h-3" />}
                </button>
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
