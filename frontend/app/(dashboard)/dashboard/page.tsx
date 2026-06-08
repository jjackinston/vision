"use client";

import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import {
  TrendingUp, TrendingDown, AlertTriangle, CheckCircle2,
  ArrowRight, Zap, Brain, RefreshCw, Sparkles,
  Package, DollarSign, BarChart3, Target, FileText, type LucideIcon,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { RevenueChart } from "@/components/charts/RevenueChart";
import { ProfitChart } from "@/components/charts/ProfitChart";
import { AIScoreCard } from "@/components/modules/AIScoreCard";
import { ActionCard } from "@/components/modules/ActionCard";
import { MetricCard } from "@/components/modules/MetricCard";
import { AgentStatusPanel } from "@/components/agents/AgentStatusPanel";
import { useCEODashboard } from "@/hooks/useCEODashboard";
import { api } from "@/lib/api";
import { downloadBriefingPDF } from "@/lib/pdf";

const containerVariants = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.05 } },
};

const itemVariants = {
  hidden: { opacity: 0, y: 16 },
  show: { opacity: 1, y: 0 },
};

function fmt(n: number, prefix = "$") {
  if (n >= 1000) return `${prefix}${(n / 1000).toFixed(1)}k`;
  return `${prefix}${n.toFixed(0)}`;
}

export default function AICEODashboard() {
  const { recommendations, summary, isLoading: aiLoading, refetch } = useCEODashboard();
  const [period, setPeriod] = useState("30d");

  const { data: overview } = useQuery({
    queryKey: ["analytics-overview", period],
    queryFn: () => api.getAnalytics(period),
    staleTime: 1000 * 60 * 5,
  });

  const metrics: Array<{ label: string; value: string; change: number; icon: LucideIcon; color: "emerald" | "violet" | "blue" | "amber" }> = [
    {
      label: `Revenue (${period})`,
      value: overview ? fmt(overview.revenue) : "$—",
      change: overview?.revenue_change ?? 0,
      icon: DollarSign,
      color: "emerald",
    },
    {
      label: "Net Profit",
      value: overview ? fmt(overview.profit) : "$—",
      change: overview?.profit_change ?? 0,
      icon: TrendingUp,
      color: "violet",
    },
    {
      label: "Units Sold",
      value: overview ? String(overview.units_sold) : "—",
      change: 0,
      icon: Package,
      color: "blue",
    },
    {
      label: "Avg ACoS",
      value: overview ? `${overview.acos}%` : "—%",
      change: 0,
      icon: Target,
      color: "amber",
    },
  ];

  // Use live recommendations if available, else fall back to sample actions
  const actions = (recommendations && recommendations.length > 0)
    ? recommendations.slice(0, 6).map((r: any) => ({
        priority: r.priority ?? "medium",
        action: r.action,
        detail: r.detail ?? r.reasoning ?? "",
        impact: r.impact ?? r.expected_impact ?? "",
        icon: r.icon ?? "zap",
      }))
    : SAMPLE_ACTIONS.slice(0, 6);

  const handleDownloadBriefing = async () => {
    await downloadBriefingPDF({
      period,
      kpis: metrics.map((m) => ({
        label:    m.label,
        value:    m.value,
        change:   m.change !== 0 ? `${m.change > 0 ? "+" : ""}${m.change}%` : "",
        positive: m.change >= 0,
      })),
      recommendations: actions.slice(0, 5).map((a: any) => ({
        priority: a.priority ?? "medium",
        action:   a.action,
        impact:   a.impact ?? a.detail ?? "",
      })),
      agentStatus: [
        { name: "Product Research Agent", status: "running", runs: 1247 },
        { name: "Trend Detection Agent",  status: "running", runs: 832  },
        { name: "Competitor Analysis",    status: "running", runs: 2104 },
        { name: "Inventory Planning",     status: "alert",   runs: 3891 },
        { name: "PPC Optimization",       status: "idle",    runs: 912  },
        { name: "Supplier Intelligence",  status: "idle",    runs: 234  },
        { name: "Listing Optimization",   status: "running", runs: 1567 },
      ],
      filename: `sv-briefing-${period}-${new Date().toISOString().slice(0, 10)}.pdf`,
    });
  };

  return (
    <div className="p-6 max-w-[1600px] mx-auto">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between mb-8"
      >
        <div>
          <div className="flex items-center gap-2 mb-1">
            <div className="w-6 h-6 rounded-md bg-gradient-to-br from-violet-500 to-blue-500 flex items-center justify-center">
              <Brain className="w-3.5 h-3.5 text-white" />
            </div>
            <h1 className="text-xl font-bold text-white">AI CEO Dashboard</h1>
            <Badge className="bg-violet-500/20 text-violet-300 border-0 text-xs">
              <Sparkles className="w-2.5 h-2.5 mr-1" />
              Live Intelligence
            </Badge>
          </div>
          <p className="text-sm text-white/40">
            {new Date().toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric" })} •
            Business health score: <span className="text-emerald-400 font-semibold">
              {overview ? Math.min(100, Math.round((overview.roi / 100) * 72 + 20)) : 72}/100
            </span>
          </p>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex rounded-lg border border-white/10 overflow-hidden">
            {["7d", "30d", "90d"].map((p) => (
              <button
                key={p}
                onClick={() => setPeriod(p)}
                className={`px-3 py-1.5 text-xs font-medium transition-colors ${
                  period === p
                    ? "bg-violet-500/20 text-violet-300"
                    : "text-white/40 hover:text-white hover:bg-white/5"
                }`}
              >
                {p}
              </button>
            ))}
          </div>
          <Button
            onClick={handleDownloadBriefing}
            variant="outline"
            size="sm"
            className="border-white/10 bg-white/5 text-white/60 hover:text-white hover:bg-white/10"
          >
            <FileText className="w-3.5 h-3.5 mr-1.5" />
            Download Briefing
          </Button>
          <Button
            onClick={() => refetch()}
            variant="outline"
            size="sm"
            className="border-white/10 bg-white/5 text-white/60 hover:text-white hover:bg-white/10"
          >
            <RefreshCw className="w-3.5 h-3.5 mr-1.5" />
            Refresh AI Analysis
          </Button>
        </div>
      </motion.div>

      {/* KPI Metrics */}
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="show"
        className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6"
      >
        {metrics.map((metric) => (
          <motion.div key={metric.label} variants={itemVariants}>
            <MetricCard {...metric} />
          </motion.div>
        ))}
      </motion.div>

      {/* Charts + AI Actions row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        {/* Revenue chart */}
        <motion.div
          variants={itemVariants}
          initial="hidden"
          animate="show"
          className="lg:col-span-2 bg-[#111218] border border-white/5 rounded-xl p-5"
        >
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-white">Revenue & Profit</h3>
              <p className="text-xs text-white/40">Last {period} — live from DB</p>
            </div>
          </div>
          <RevenueChart period={period} />
        </motion.div>

        {/* AI Score Cards */}
        <motion.div
          variants={itemVariants}
          initial="hidden"
          animate="show"
          className="space-y-3"
        >
          <AIScoreCard
            title="Business Health"
            score={overview ? Math.min(100, Math.round(overview.roi * 0.7 + 20)) : 72}
            trend={overview?.revenue_change ?? 4}
            description={overview ? `${overview.acos}% ACoS · ${overview.units_sold} units sold` : "Loading…"}
            color="emerald"
          />
          <AIScoreCard
            title="Opportunity Score"
            score={84}
            trend={+12}
            description="5 high-margin opportunities detected this week"
            color="violet"
          />
          <AIScoreCard
            title="Risk Level"
            score={31}
            trend={-8}
            description="2 products approaching stockout in 14 days"
            color="amber"
            invertScore
          />
        </motion.div>
      </div>

      {/* AI CEO Action Items */}
      <motion.div
        variants={itemVariants}
        initial="hidden"
        animate="show"
        className="bg-[#111218] border border-white/5 rounded-xl p-5 mb-6"
      >
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Zap className="w-4 h-4 text-amber-400" />
            <h3 className="text-sm font-semibold text-white">Today's AI Action Plan</h3>
            <Badge className="bg-amber-500/20 text-amber-400 border-0 text-xs">
              {actions.length} actions
            </Badge>
          </div>
          <Button variant="ghost" size="sm" className="text-xs text-white/40 hover:text-white">
            View all <ArrowRight className="w-3 h-3 ml-1" />
          </Button>
        </div>

        {aiLoading ? (
          <div className="text-xs text-white/20 py-4 text-center">Loading AI recommendations…</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
            {actions.map((action: any, i: number) => (
              <ActionCard key={i} action={action} index={i} />
            ))}
          </div>
        )}
      </motion.div>

      {/* Bottom row: Agents + Profit chart */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div variants={itemVariants} initial="hidden" animate="show">
          <AgentStatusPanel />
        </motion.div>
        <motion.div
          variants={itemVariants}
          initial="hidden"
          animate="show"
          className="bg-[#111218] border border-white/5 rounded-xl p-5"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-white">Profit by Platform</h3>
            <BarChart3 className="w-4 h-4 text-white/30" />
          </div>
          <ProfitChart period={period} />
        </motion.div>
      </div>
    </div>
  );
}

const SAMPLE_ACTIONS: Array<{ priority: "critical" | "high" | "medium" | "low"; action: string; detail: string; impact: string; icon: string }> = [
  {
    priority: "critical",
    action: "Reorder 500 units of Product B",
    detail: "Stockout predicted in 11 days. Lead time: 28 days.",
    impact: "+$8,400 avoided lost revenue",
    icon: "package",
  },
  {
    priority: "high",
    action: "Increase price on Widget Pro by 7%",
    detail: "Buy box held at current price. Competitors 12% higher.",
    impact: "+$1,200/mo estimated profit",
    icon: "dollar",
  },
  {
    priority: "high",
    action: "Pause 3 high-ACoS keywords",
    detail: "Keywords: 'premium widget set', 'deluxe gadget', 'pro organizer'",
    impact: "-$340/mo wasted ad spend",
    icon: "target",
  },
  {
    priority: "medium",
    action: "Expand Gadget X to Walmart Marketplace",
    detail: "Walmart demand score: 78/100. Competition: Low.",
    impact: "+$3,200/mo projected revenue",
    icon: "globe",
  },
  {
    priority: "medium",
    action: "Optimize 7 listings below SEO score 70",
    detail: "Missing target keywords in titles. Avg score: 52/100.",
    impact: "+15-25% organic traffic est.",
    icon: "file",
  },
  {
    priority: "low",
    action: "Request quote from 2 backup suppliers",
    detail: "Current supplier lead time increased to 35 days.",
    impact: "Risk mitigation",
    icon: "warehouse",
  },
];
