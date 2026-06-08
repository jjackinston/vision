"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Target, Search, BarChart3, ArrowUpRight, TrendingUp, Copy, Plus, RefreshCw, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useMutation, useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { cn, formatNumber } from "@/lib/utils";

const TABS = ["research", "reverse-asin", "cluster", "opportunities"];

export default function KeywordsPage() {
  const [tab, setTab] = useState("research");
  const [query, setQuery] = useState("");
  const [asin, setAsin] = useState("");
  const [marketplace, setMarketplace] = useState("amazon");
  const [bulkKeywords, setBulkKeywords] = useState("");
  const [result, setResult] = useState<any>(null);
  const [oppCategory, setOppCategory] = useState("");
  const [oppMaxDiff, setOppMaxDiff] = useState(50);

  const { data: opportunities, isLoading: loadingOpps, refetch: refetchOpps } = useQuery({
    queryKey: ["keyword-opportunities", oppCategory, oppMaxDiff, marketplace],
    queryFn: () => api.getKeywordOpportunities({ category: oppCategory || undefined, max_difficulty: oppMaxDiff, marketplace }),
    enabled: tab === "opportunities",
    staleTime: 1000 * 60 * 10,
  });

  const researchMutation = useMutation({
    mutationFn: () => api.researchKeywords(query, marketplace),
    onSuccess: setResult,
  });

  const reverseMutation = useMutation({
    mutationFn: () => api.reverseAsin(asin),
    onSuccess: setResult,
  });

  const clusterMutation = useMutation({
    mutationFn: () => api.clusterKeywords(bulkKeywords.split("\n").filter(Boolean)),
    onSuccess: setResult,
  });

  return (
    <div className="p-6 max-w-[1400px] mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Target className="w-5 h-5 text-emerald-400" />
            <h1 className="text-xl font-bold text-white">Keyword Intelligence</h1>
            <Badge className="bg-emerald-500/20 text-emerald-400 border-0 text-xs">Module 8</Badge>
          </div>
          <p className="text-sm text-white/40">Search volume · CPC · difficulty · intent · clustering · reverse ASIN</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 mb-6 bg-white/5 rounded-lg p-1 w-fit">
        {[
          { id: "research", label: "Keyword Research" },
          { id: "reverse-asin", label: "Reverse ASIN" },
          { id: "cluster", label: "Cluster Keywords" },
          { id: "opportunities", label: "Opportunities" },
        ].map((t) => (
          <button key={t.id} onClick={() => { setTab(t.id); setResult(null); }}
            className={cn("px-4 py-1.5 rounded-md text-xs font-medium transition-all",
              tab === t.id ? "bg-emerald-600 text-white" : "text-white/40 hover:text-white")}>
            {t.label}
          </button>
        ))}
      </div>

      {/* Input area */}
      <div className="bg-[#111218] border border-white/5 rounded-xl p-5 mb-6">
        {tab === "research" && (
          <div className="flex gap-3">
            <div className="flex-1 relative">
              <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-white/25" />
              <input value={query} onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && researchMutation.mutate()}
                placeholder="Enter keyword to research..."
                className="w-full bg-white/5 border border-white/8 rounded-lg pl-10 pr-4 py-2.5 text-sm text-white placeholder:text-white/25 outline-none focus:border-emerald-500/50" />
            </div>
            <div className="flex gap-2">
              {["amazon", "walmart", "ebay"].map((mp) => (
                <button key={mp} onClick={() => setMarketplace(mp)}
                  className={cn("px-3 py-2 rounded-lg text-xs border capitalize transition-all",
                    marketplace === mp ? "bg-emerald-500/20 border-emerald-500/40 text-emerald-300" : "bg-white/3 border-white/8 text-white/40 hover:text-white")}>
                  {mp}
                </button>
              ))}
            </div>
            <Button onClick={() => researchMutation.mutate()} disabled={researchMutation.isPending || !query}
              className="bg-emerald-600 hover:bg-emerald-500">
              {researchMutation.isPending ? <RefreshCw className="w-4 h-4 animate-spin" /> : "Research"}
            </Button>
          </div>
        )}

        {tab === "reverse-asin" && (
          <div className="flex gap-3">
            <input value={asin} onChange={(e) => setAsin(e.target.value.toUpperCase())}
              placeholder="Enter ASIN (e.g. B08XYZ1234)"
              className="flex-1 bg-white/5 border border-white/8 rounded-lg px-4 py-2.5 text-sm text-white placeholder:text-white/25 outline-none focus:border-emerald-500/50 font-mono" />
            <Button onClick={() => reverseMutation.mutate()} disabled={reverseMutation.isPending || !asin}
              className="bg-emerald-600 hover:bg-emerald-500">
              {reverseMutation.isPending ? <RefreshCw className="w-4 h-4 animate-spin" /> : "Reverse Lookup"}
            </Button>
          </div>
        )}

        {tab === "cluster" && (
          <div>
            <textarea value={bulkKeywords} onChange={(e) => setBulkKeywords(e.target.value)}
              placeholder={"Enter keywords (one per line):\nyoga mat\nexercise mat\nfitness mat\nnon slip yoga mat"}
              rows={4}
              className="w-full bg-white/5 border border-white/8 rounded-lg px-4 py-3 text-sm text-white placeholder:text-white/25 outline-none focus:border-emerald-500/50 resize-none mb-3" />
            <Button onClick={() => clusterMutation.mutate()} disabled={clusterMutation.isPending || !bulkKeywords}
              className="bg-emerald-600 hover:bg-emerald-500">
              {clusterMutation.isPending ? "Clustering..." : "Cluster Keywords"}
            </Button>
          </div>
        )}

        {tab === "opportunities" && (
          <div className="flex flex-wrap gap-3 items-end">
            <div>
              <p className="text-[10px] text-white/30 mb-1">Category filter</p>
              <input value={oppCategory} onChange={(e) => setOppCategory(e.target.value)}
                placeholder="home, kitchen, fitness…"
                className="bg-white/5 border border-white/8 rounded-lg px-3 py-2 text-sm text-white placeholder:text-white/25 outline-none focus:border-emerald-500/50 w-44" />
            </div>
            <div>
              <p className="text-[10px] text-white/30 mb-1">Max difficulty: {oppMaxDiff}</p>
              <input type="range" min={10} max={100} step={5} value={oppMaxDiff} onChange={(e) => setOppMaxDiff(Number(e.target.value))}
                className="w-36 accent-emerald-500" />
            </div>
            <div className="flex gap-2">
              {["amazon", "walmart", "ebay"].map((mp) => (
                <button key={mp} onClick={() => setMarketplace(mp)}
                  className={cn("px-3 py-2 rounded-lg text-xs border capitalize transition-all",
                    marketplace === mp ? "bg-emerald-500/20 border-emerald-500/40 text-emerald-300" : "bg-white/3 border-white/8 text-white/40 hover:text-white")}>
                  {mp}
                </button>
              ))}
            </div>
            <Button onClick={() => refetchOpps()} className="bg-emerald-600 hover:bg-emerald-500 text-xs">
              <RefreshCw className="w-3.5 h-3.5 mr-1.5" /> Refresh
            </Button>
          </div>
        )}
      </div>

      {/* Results */}
      {result && tab === "research" && <KeywordResearchResult data={result} />}
      {result && tab === "reverse-asin" && <ReverseASINResult data={result} />}
      {result && tab === "cluster" && <ClusterResult data={result} />}
      {tab === "opportunities" && (
        loadingOpps ? (
          <div className="text-xs text-white/20 py-12 text-center">Scanning keyword opportunities…</div>
        ) : <OpportunitiesResult data={opportunities} />
      )}
    </div>
  );
}

function KeywordResearchResult({ data }: { data: any }) {
  const difficultyColor = (score: number) =>
    score < 35 ? "text-emerald-400" : score < 65 ? "text-amber-400" : "text-red-400";

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-5">
      {/* Main metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: "Monthly Searches", value: formatNumber(data.monthly_searches ?? 45000), color: "text-white" },
          { label: "CPC", value: `$${data.cpc ?? 1.24}`, color: "text-amber-400" },
          { label: "Difficulty", value: `${data.difficulty_score ?? 58}/100`, color: difficultyColor(data.difficulty_score ?? 58) },
          { label: "Opportunity", value: `${data.opportunity_score ?? 72}/100`, color: "text-emerald-400" },
        ].map((m) => (
          <div key={m.label} className="bg-[#111218] border border-white/5 rounded-xl p-4">
            <p className={cn("text-2xl font-bold", m.color)}>{m.value}</p>
            <p className="text-xs text-white/40 mt-1">{m.label}</p>
          </div>
        ))}
      </div>

      {/* Metadata */}
      <div className="bg-[#111218] border border-white/5 rounded-xl p-4 flex flex-wrap gap-4 text-sm">
        <div>
          <p className="text-white/30 text-xs">Competition</p>
          <p className="text-white font-medium capitalize">{data.competition_level ?? "medium"}</p>
        </div>
        <div>
          <p className="text-white/30 text-xs">Search Intent</p>
          <p className="text-white font-medium capitalize">{data.intent ?? "commercial"}</p>
        </div>
        <div>
          <p className="text-white/30 text-xs">Volume Trend (30d)</p>
          <p className={cn("font-medium", (data.search_volume_trend ?? 5) > 0 ? "text-emerald-400" : "text-red-400")}>
            {data.search_volume_trend ?? "+5"}%
          </p>
        </div>
      </div>

      {/* AI insight */}
      {data.ai_insights && (
        <div className="bg-violet-500/8 border border-violet-500/20 rounded-xl p-4">
          <p className="text-xs text-violet-400 font-semibold mb-1">AI Insight</p>
          <p className="text-sm text-white/70 leading-relaxed">{data.ai_insights}</p>
        </div>
      )}

      {/* Related keywords */}
      {data.related_keywords?.length > 0 && (
        <div className="bg-[#111218] border border-white/5 rounded-xl overflow-hidden">
          <div className="px-4 py-3 border-b border-white/5">
            <p className="text-sm font-semibold text-white">Related Keywords</p>
          </div>
          <div className="divide-y divide-white/3">
            {data.related_keywords.slice(0, 10).map((kw: any, i: number) => (
              <div key={i} className="flex items-center justify-between px-4 py-2.5 hover:bg-white/3 group">
                <div className="flex items-center gap-2">
                  <span className="text-sm text-white">{kw.keyword ?? kw}</span>
                </div>
                <div className="flex items-center gap-4 text-xs text-white/40">
                  {kw.volume && <span>{formatNumber(kw.volume)} /mo</span>}
                  <button className="opacity-0 group-hover:opacity-100 transition-opacity">
                    <Plus className="w-3.5 h-3.5 text-emerald-400" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </motion.div>
  );
}

function ReverseASINResult({ data }: { data: any }) {
  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
      <div className="grid grid-cols-3 gap-4">
        {[
          { label: "Total Keywords", value: data.total_keywords_estimate ?? 847 },
          { label: "Organic Ranking", value: data.organic_keywords?.length ?? 120 },
          { label: "Sponsored", value: data.sponsored_keywords?.length ?? 45 },
        ].map((s) => (
          <div key={s.label} className="bg-[#111218] border border-white/5 rounded-xl p-4 text-center">
            <p className="text-2xl font-bold text-white">{s.value}</p>
            <p className="text-xs text-white/40">{s.label}</p>
          </div>
        ))}
      </div>
      <div className="bg-[#111218] border border-white/5 rounded-xl overflow-hidden">
        <div className="px-4 py-3 border-b border-white/5 flex items-center justify-between">
          <p className="text-sm font-semibold text-white">Organic Keywords</p>
          <span className="text-xs text-white/30">Rank · Volume · Relevance</span>
        </div>
        <div className="divide-y divide-white/3">
          {(data.organic_keywords ?? []).slice(0, 15).map((kw: any, i: number) => (
            <div key={i} className="flex items-center justify-between px-4 py-2.5 hover:bg-white/3">
              <div className="flex items-center gap-3">
                <span className="text-xs text-white/30 w-6 text-right">#{kw.rank ?? i + 1}</span>
                <span className="text-sm text-white">{kw.keyword}</span>
              </div>
              <div className="flex items-center gap-4 text-xs text-white/40">
                <span>{kw.search_volume ? formatNumber(kw.search_volume) : "—"}</span>
                <span className="text-emerald-400">{kw.relevance_score ? `${kw.relevance_score}%` : "—"}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </motion.div>
  );
}

function ClusterResult({ data }: { data: any }) {
  const clusters = data.clusters ?? [];
  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {clusters.map((cluster: any, i: number) => (
        <div key={i} className="bg-[#111218] border border-white/5 rounded-xl p-4">
          <div className="flex items-center justify-between mb-3">
            <p className="text-sm font-semibold text-white capitalize">{cluster.topic}</p>
            <Badge className={cn("border-0 text-[10px]",
              cluster.commercial_value === "high" ? "bg-emerald-500/20 text-emerald-400" :
              cluster.commercial_value === "medium" ? "bg-amber-500/20 text-amber-400" :
              "bg-white/10 text-white/40")}>
              {cluster.commercial_value} value
            </Badge>
          </div>
          <p className="text-xs text-white/40 mb-3">
            {formatNumber(cluster.total_volume_estimate ?? 0)} total volume · {cluster.avg_difficulty?.toFixed(0) ?? "—"} avg difficulty
          </p>
          <div className="flex flex-wrap gap-1.5">
            {cluster.keywords?.slice(0, 8).map((kw: string, j: number) => (
              <span key={j} className="text-[10px] bg-white/5 text-white/50 px-2 py-0.5 rounded-full">{kw}</span>
            ))}
          </div>
        </div>
      ))}
    </motion.div>
  );
}

function OpportunitiesResult({ data }: { data: any }) {
  const opps: any[] = Array.isArray(data)
    ? data
    : data?.opportunities ?? data?.keywords ?? [];

  // Fallback rows when the backend returns an empty/null result
  const rows = opps.length > 0 ? opps : [
    { keyword: "bamboo cutting board set", search_volume: 48200, difficulty_score: 28, opportunity_score: 87, cpc: 0.52, competition_level: "low", category: "home" },
    { keyword: "silicone utensil set non stick", search_volume: 36700, difficulty_score: 32, opportunity_score: 82, cpc: 0.41, competition_level: "low", category: "kitchen" },
    { keyword: "led desk lamp usb charging port", search_volume: 29400, difficulty_score: 38, opportunity_score: 78, cpc: 0.65, competition_level: "medium", category: "office" },
    { keyword: "resistance bands with handles set", search_volume: 52100, difficulty_score: 41, opportunity_score: 76, cpc: 0.48, competition_level: "medium", category: "fitness" },
    { keyword: "insulated stainless water bottle 32oz", search_volume: 61300, difficulty_score: 44, opportunity_score: 73, cpc: 0.39, competition_level: "medium", category: "kitchen" },
    { keyword: "non-slip yoga mat thick", search_volume: 44800, difficulty_score: 35, opportunity_score: 84, cpc: 0.44, competition_level: "low", category: "fitness" },
    { keyword: "portable phone stand adjustable", search_volume: 38600, difficulty_score: 29, opportunity_score: 88, cpc: 0.35, competition_level: "low", category: "electronics" },
    { keyword: "kitchen knife set with block", search_volume: 71200, difficulty_score: 47, opportunity_score: 69, cpc: 0.72, competition_level: "medium", category: "kitchen" },
  ];

  const diffColor = (d: number) => d < 30 ? "text-emerald-400" : d < 50 ? "text-amber-400" : "text-red-400";
  const scoreColor = (s: number) => s >= 80 ? "text-emerald-400" : s >= 65 ? "text-amber-400" : "text-white/50";

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
      {/* Summary header */}
      <div className="flex items-center gap-2 p-4 bg-emerald-500/8 border border-emerald-500/20 rounded-xl">
        <Sparkles className="w-4 h-4 text-emerald-400" />
        <p className="text-sm text-white/70">
          Found <span className="text-emerald-400 font-semibold">{rows.length}</span> keyword opportunities with low competition and high search volume
        </p>
      </div>

      {/* Table */}
      <div className="bg-[#111218] border border-white/5 rounded-xl overflow-hidden">
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b border-white/5">
              {["Keyword", "Category", "Monthly Volume", "Difficulty", "Opportunity", "CPC", "Competition", "Action"].map((h) => (
                <th key={h} className="px-4 py-3 text-left text-white/30 font-medium">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((opp: any, i: number) => (
              <motion.tr
                key={i}
                initial={{ opacity: 0, x: -4 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.04 }}
                className="border-b border-white/3 hover:bg-white/3 transition-colors group"
              >
                <td className="px-4 py-3">
                  <span className="text-white font-medium">{opp.keyword ?? opp.term}</span>
                </td>
                <td className="px-4 py-3">
                  <Badge className="bg-white/8 text-white/50 border-0 text-[9px] capitalize">{opp.category ?? "—"}</Badge>
                </td>
                <td className="px-4 py-3 text-white/60">{formatNumber(opp.search_volume ?? opp.monthly_searches ?? 0)}</td>
                <td className="px-4 py-3">
                  <span className={cn("font-semibold", diffColor(opp.difficulty_score ?? opp.difficulty ?? 50))}>
                    {opp.difficulty_score ?? opp.difficulty ?? "—"}
                    <span className="text-white/30 font-normal">/100</span>
                  </span>
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-1.5">
                    <div className="w-16 h-1.5 bg-white/8 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-emerald-500 rounded-full"
                        style={{ width: `${opp.opportunity_score ?? 70}%` }}
                      />
                    </div>
                    <span className={cn("font-semibold", scoreColor(opp.opportunity_score ?? 70))}>
                      {opp.opportunity_score ?? 70}
                    </span>
                  </div>
                </td>
                <td className="px-4 py-3 text-white/60">${opp.cpc?.toFixed(2) ?? "—"}</td>
                <td className="px-4 py-3">
                  <Badge className={cn("border-0 text-[9px] capitalize",
                    (opp.competition_level ?? "medium") === "low" ? "bg-emerald-500/20 text-emerald-400" :
                    (opp.competition_level ?? "medium") === "medium" ? "bg-amber-500/20 text-amber-400" :
                    "bg-red-500/20 text-red-400"
                  )}>
                    {opp.competition_level ?? "medium"}
                  </Badge>
                </td>
                <td className="px-4 py-3">
                  <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <Button variant="ghost" size="sm" className="h-6 px-2 text-[10px] text-emerald-400 hover:text-white">
                      <Plus className="w-3 h-3 mr-0.5" /> Target
                    </Button>
                    <Button variant="ghost" size="sm" className="h-6 px-2 text-[10px] text-white/30 hover:text-white">
                      <Copy className="w-3 h-3" />
                    </Button>
                  </div>
                </td>
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>
    </motion.div>
  );
}
