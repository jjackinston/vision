"use client";

import { useQuery } from "@tanstack/react-query";
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer,
} from "recharts";
import { api } from "@/lib/api";

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload) return null;
  return (
    <div className="bg-[#1A1B22] border border-white/10 rounded-lg p-3 shadow-xl">
      <p className="text-xs text-white/50 mb-2">{label}</p>
      {payload.map((p: any) => (
        <div key={p.name} className="flex items-center gap-2 text-xs">
          <div className="w-2 h-2 rounded-full" style={{ background: p.color }} />
          <span className="text-white/60 capitalize">{p.name}:</span>
          <span className="text-white font-semibold">${p.value.toLocaleString()}</span>
        </div>
      ))}
    </div>
  );
};

function formatDate(dateStr: string) {
  const d = new Date(dateStr);
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

export function RevenueChart({ period = "30d" }: { period?: string }) {
  const { data, isLoading } = useQuery({
    queryKey: ["revenue-series", period],
    queryFn: () => api.getRevenueSeries(period),
    staleTime: 1000 * 60 * 5,
  });

  const chartData = (data ?? []).map((row: any) => ({
    date: formatDate(row.date),
    revenue: Math.round(row.revenue),
    profit: Math.round(row.profit),
    adSpend: Math.round(row.ad_spend),
  }));

  if (isLoading || chartData.length === 0) {
    return (
      <div className="h-[220px] flex items-center justify-center">
        <div className="text-xs text-white/20">{isLoading ? "Loading…" : "No data"}</div>
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={220}>
      <AreaChart data={chartData} margin={{ top: 5, right: 5, bottom: 0, left: -10 }}>
        <defs>
          <linearGradient id="revenue" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#8B5CF6" stopOpacity={0.3} />
            <stop offset="95%" stopColor="#8B5CF6" stopOpacity={0} />
          </linearGradient>
          <linearGradient id="profit" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#10B981" stopOpacity={0.3} />
            <stop offset="95%" stopColor="#10B981" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
        <XAxis dataKey="date" tick={{ fontSize: 11, fill: "rgba(255,255,255,0.3)" }} tickLine={false} axisLine={false} />
        <YAxis tick={{ fontSize: 11, fill: "rgba(255,255,255,0.3)" }} tickLine={false} axisLine={false} tickFormatter={(v) => `$${(v / 1000).toFixed(1)}k`} />
        <Tooltip content={<CustomTooltip />} />
        <Area type="monotone" dataKey="revenue" stroke="#8B5CF6" strokeWidth={2} fill="url(#revenue)" name="revenue" />
        <Area type="monotone" dataKey="profit" stroke="#10B981" strokeWidth={2} fill="url(#profit)" name="profit" />
      </AreaChart>
    </ResponsiveContainer>
  );
}
