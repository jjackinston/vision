"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Bot, Play, Pause, RefreshCw, Terminal, Zap, Plus, Settings2, MessageSquare } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";
import { AgentChatPanel } from "@/components/agents/AgentChatPanel";
import { toast } from "sonner";

const agents = [
  {
    id: "product_research",
    name: "Product Research Agent",
    description: "Continuously scans all marketplaces for high-opportunity products. Analyzes demand, competition, margins, and trends in real-time.",
    status: "running",
    model: "GPT-4o",
    runCount: 1247,
    lastFindings: 12,
    avgRuntime: "38s",
    tools: ["Amazon Search", "Keyword Analysis", "Opportunity Scoring"],
    color: "violet",
  },
  {
    id: "trend",
    name: "Trend Detection Agent",
    description: "Monitors Google Trends, TikTok, Reddit, Pinterest, and YouTube for emerging product opportunities before they go mainstream.",
    status: "running",
    model: "GPT-4o",
    runCount: 832,
    lastFindings: 5,
    avgRuntime: "52s",
    tools: ["Google Trends", "TikTok Monitor", "Reddit Scanner"],
    color: "blue",
  },
  {
    id: "competitor",
    name: "Competitor Analysis Agent",
    description: "Analyzes competitor reviews, pricing, listings, and inventory to detect weaknesses and generate competitive advantages.",
    status: "running",
    model: "Claude 3.5",
    runCount: 2104,
    lastFindings: 8,
    avgRuntime: "1m 12s",
    tools: ["Review Mining", "Price Tracker", "Listing Analyzer"],
    color: "amber",
  },
  {
    id: "inventory",
    name: "Inventory Planning Agent",
    description: "Predicts stockouts and overstock events before they occur. Generates automated reorder recommendations based on sales velocity.",
    status: "alert",
    model: "GPT-4o",
    runCount: 3891,
    lastFindings: 2,
    avgRuntime: "18s",
    tools: ["Stock Monitor", "Sales Velocity", "Reorder Engine"],
    color: "red",
    alert: "2 products predicted stockout in <14 days",
  },
  {
    id: "ppc",
    name: "PPC Optimization Agent",
    description: "Continuously optimizes advertising campaigns for maximum ROAS. Harvests keywords, pauses underperformers, adjusts bids.",
    status: "idle",
    model: "GPT-4o",
    runCount: 912,
    lastFindings: 3,
    avgRuntime: "2m 5s",
    tools: ["Campaign Monitor", "Bid Optimizer", "Keyword Harvester"],
    color: "emerald",
  },
  {
    id: "supplier",
    name: "Supplier Intelligence Agent",
    description: "Monitors supplier performance, costs, lead times, and geopolitical risks. Generates negotiation opportunities.",
    status: "idle",
    model: "Claude 3.5",
    runCount: 234,
    lastFindings: 1,
    avgRuntime: "1m 44s",
    tools: ["Supplier Tracker", "Cost Analyzer", "Risk Monitor"],
    color: "pink",
  },
  {
    id: "listing",
    name: "Listing Optimization Agent",
    description: "Maintains peak-performing listings across all platforms. Monitors keyword rankings, CTR, and conversion to auto-optimize.",
    status: "running",
    model: "Claude 3.5",
    runCount: 1567,
    lastFindings: 7,
    avgRuntime: "1m 28s",
    tools: ["Listing Analyzer", "SEO Optimizer", "A/B Tester"],
    color: "sky",
  },
];

const colorMap: Record<string, { bg: string; text: string; dot: string }> = {
  violet: { bg: "bg-violet-500/10", text: "text-violet-400", dot: "bg-violet-500" },
  blue: { bg: "bg-blue-500/10", text: "text-blue-400", dot: "bg-blue-500" },
  amber: { bg: "bg-amber-500/10", text: "text-amber-400", dot: "bg-amber-500" },
  red: { bg: "bg-red-500/10", text: "text-red-400", dot: "bg-red-500" },
  emerald: { bg: "bg-emerald-500/10", text: "text-emerald-400", dot: "bg-emerald-500" },
  pink: { bg: "bg-pink-500/10", text: "text-pink-400", dot: "bg-pink-500" },
  sky: { bg: "bg-sky-500/10", text: "text-sky-400", dot: "bg-sky-500" },
};

export default function AgentsPage() {
  const [view, setView] = useState<"fleet" | "chat">("fleet");
  const [selected, setSelected] = useState<string | null>(null);
  const [paused, setPaused] = useState<Set<string>>(new Set());

  const { data: liveAgents } = useQuery({
    queryKey: ["agents-list"],
    queryFn: () => api.getAgents(),
    staleTime: 1000 * 10,
    refetchInterval: 1000 * 10,
  });

  // Merge live status/findings/run stats into static agent definitions
  const mergedAgents = agents.map((a) => {
    const live = (liveAgents as any[])?.find((l: any) => l.id === a.id);
    return {
      ...a,
      status: live?.status ?? a.status,
      lastFindings: live?.findings ?? live?.last_findings ?? a.lastFindings,
      runCount: live?.run_count ?? live?.runCount ?? a.runCount,
      avgRuntime: live?.avg_runtime ?? live?.avgRuntime ?? a.avgRuntime,
    };
  });

  const queryClient = useQueryClient();
  const runMutation = useMutation({
    mutationFn: (agentId: string) => api.runAgent(agentId, {}),
    onSuccess: (_: any, agentId: string) => {
      setTimeout(() => queryClient.invalidateQueries({ queryKey: ["agents-list"] }), 2000);
      const name = agents.find((a) => a.id === agentId)?.name ?? "Agent";
      toast.success(`${name} queued successfully`);
    },
    onError: () => toast.error("Failed to queue agent run"),
  });

  const toggle = (id: string) => {
    setPaused(prev => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  const running = mergedAgents.filter(a => a.status === "running" && !paused.has(a.id)).length;

  return (
    <div className="p-6 max-w-[1400px] mx-auto">
      <div className="flex items-center justify-between mb-8">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Bot className="w-5 h-5 text-violet-400" />
            <h1 className="text-xl font-bold text-white">AI Agent Fleet</h1>
            <Badge className="bg-emerald-500/20 text-emerald-400 border-0">
              {running} running
            </Badge>
          </div>
          <p className="text-sm text-white/40">Autonomous AI agents collaborating 24/7 to grow your business</p>
        </div>
        <div className="flex gap-2">
          <div className="flex gap-1 bg-white/5 rounded-lg p-1">
            {([
              { id: "fleet", label: "Fleet",       icon: Bot },
              { id: "chat",  label: "Chat",         icon: MessageSquare },
            ] as const).map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                onClick={() => setView(id)}
                className={cn(
                  "flex items-center gap-1.5 px-3 py-1 rounded-md text-xs font-medium transition-all",
                  view === id ? "bg-violet-600 text-white" : "text-white/40 hover:text-white"
                )}
              >
                <Icon className="w-3.5 h-3.5" />
                {label}
              </button>
            ))}
          </div>
          <Button variant="outline" size="sm" className="border-white/10 bg-white/5 text-white/60 hover:text-white">
            <Terminal className="w-3.5 h-3.5 mr-1.5" />
            Logs
          </Button>
          <Button size="sm" className="bg-violet-600 hover:bg-violet-500">
            <Plus className="w-3.5 h-3.5 mr-1.5" />
            Custom
          </Button>
        </div>
      </div>

      {view === "chat" && (
        <AgentChatPanel />
      )}

      {view === "fleet" && <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {mergedAgents.map((agent, i) => {
          const colors = colorMap[agent.color];
          const isPaused = paused.has(agent.id);
          const isSelected = selected === agent.id;

          return (
            <motion.div
              key={agent.id}
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              onClick={() => setSelected(isSelected ? null : agent.id)}
              className={cn(
                "bg-[#111218] border rounded-xl p-5 cursor-pointer transition-all duration-200",
                isSelected ? "border-violet-500/40 shadow-lg shadow-violet-500/10" : "border-white/5 hover:border-white/15"
              )}
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className={cn("w-9 h-9 rounded-xl flex items-center justify-center", colors.bg)}>
                    <Zap className={cn("w-4 h-4", colors.text)} />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-white leading-none mb-1">{agent.name}</p>
                    <div className="flex items-center gap-1.5">
                      <div className={cn(
                        "w-1.5 h-1.5 rounded-full",
                        agent.status === "alert" ? "bg-red-500 animate-pulse" :
                        isPaused ? "bg-white/20" :
                        agent.status === "running" ? `${colors.dot} animate-pulse` : "bg-white/20"
                      )} />
                      <span className={cn("text-[10px]",
                        agent.status === "alert" ? "text-red-400" :
                        isPaused ? "text-white/30" :
                        agent.status === "running" ? colors.text : "text-white/30"
                      )}>
                        {agent.status === "alert" ? "Alert" : isPaused ? "Paused" : agent.status === "running" ? "Running" : "Idle"}
                      </span>
                    </div>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={(e) => { e.stopPropagation(); toggle(agent.id); }}
                  className="w-7 h-7 text-white/20 hover:text-white hover:bg-white/10"
                >
                  {isPaused ? <Play className="w-3.5 h-3.5" /> : <Pause className="w-3.5 h-3.5" />}
                </Button>
              </div>

              {agent.alert && (
                <div className="mb-3 px-3 py-2 rounded-lg bg-red-500/10 border border-red-500/20">
                  <p className="text-xs text-red-400">{agent.alert}</p>
                </div>
              )}

              <p className="text-xs text-white/40 leading-relaxed mb-4">{agent.description}</p>

              <div className="grid grid-cols-3 gap-3 mb-4">
                {[
                  { label: "Runs", value: agent.runCount.toLocaleString() },
                  { label: "Findings", value: agent.lastFindings.toString() },
                  { label: "Avg Time", value: agent.avgRuntime },
                ].map((stat) => (
                  <div key={stat.label} className="text-center">
                    <p className="text-sm font-bold text-white">{stat.value}</p>
                    <p className="text-[10px] text-white/30">{stat.label}</p>
                  </div>
                ))}
              </div>

              {isSelected && (
                <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }}>
                  <div className="border-t border-white/5 pt-4">
                    <p className="text-[10px] font-semibold uppercase text-white/30 mb-2">Tools</p>
                    <div className="flex flex-wrap gap-1.5">
                      {agent.tools.map(tool => (
                        <span key={tool} className="text-[10px] bg-white/5 text-white/40 px-2 py-0.5 rounded-full">
                          {tool}
                        </span>
                      ))}
                    </div>
                    <div className="flex gap-2 mt-3">
                      <Button
                        size="sm"
                        className="flex-1 h-7 text-xs bg-violet-600 hover:bg-violet-500"
                        onClick={(e) => { e.stopPropagation(); runMutation.mutate(agent.id); }}
                        disabled={runMutation.isPending && runMutation.variables === agent.id}
                      >
                        {runMutation.isPending && runMutation.variables === agent.id
                          ? <RefreshCw className="w-3 h-3 mr-1 animate-spin" />
                          : <Play className="w-3 h-3 mr-1" />
                        }
                        {runMutation.isPending && runMutation.variables === agent.id ? "Queuing…" : "Run Now"}
                      </Button>
                      <Button variant="outline" size="icon" className="h-7 w-7 border-white/10 bg-white/5">
                        <Settings2 className="w-3 h-3 text-white/40" />
                      </Button>
                    </div>
                  </div>
                </motion.div>
              )}
            </motion.div>
          );
        })}
      </div>}
    </div>
  );
}
