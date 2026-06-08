"use client";

import { useQuery } from "@tanstack/react-query";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts";
import { api } from "@/lib/api";

const PLATFORM_COLORS: Record<string, string> = {
  amazon: "#F59E0B",
  walmart: "#3B82F6",
  shopify: "#8B5CF6",
  ebay: "#10B981",
  tiktok: "#EC4899",
};

export function ProfitChart({ period = "30d" }: { period?: string }) {
  const { data, isLoading } = useQuery({
    queryKey: ["by-platform", period],
    queryFn: () => api.getByPlatform(period),
    staleTime: 1000 * 60 * 5,
  });

  const chartData = (data ?? []).map((row: any) => ({
    platform: row.marketplace.charAt(0).toUpperCase() + row.marketplace.slice(1),
    profit: Math.round(row.profit),
    color: PLATFORM_COLORS[row.marketplace.toLowerCase()] ?? "#6B7280",
  }));

  if (isLoading || chartData.length === 0) {
    return (
      <div className="h-[200px] flex items-center justify-center">
        <div className="text-xs text-white/20">{isLoading ? "Loading…" : "No data"}</div>
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={200}>
      <BarChart data={chartData} margin={{ top: 5, right: 5, bottom: 0, left: -15 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" vertical={false} />
        <XAxis dataKey="platform" tick={{ fontSize: 11, fill: "rgba(255,255,255,0.3)" }} tickLine={false} axisLine={false} />
        <YAxis tick={{ fontSize: 11, fill: "rgba(255,255,255,0.3)" }} tickLine={false} axisLine={false} tickFormatter={(v) => `$${(v / 1000).toFixed(1)}k`} />
        <Tooltip
          contentStyle={{ background: "#1A1B22", border: "1px solid rgba(255,255,255,0.1)", borderRadius: "8px" }}
          labelStyle={{ color: "rgba(255,255,255,0.5)", fontSize: 11 }}
          itemStyle={{ color: "#fff", fontSize: 12 }}
          formatter={(v: number) => [`$${v.toLocaleString()}`, "Net Profit"]}
        />
        <Bar dataKey="profit" radius={[4, 4, 0, 0]}>
          {chartData.map((entry: any, i: number) => (
            <Cell key={i} fill={entry.color} fillOpacity={0.8} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
