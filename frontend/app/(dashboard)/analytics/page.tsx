"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { BarChart3, TrendingUp, DollarSign, ShoppingCart, Target, Globe, Download, FileText } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { cn, formatCurrency, formatNumber } from "@/lib/utils";
import { downloadPDF } from "@/lib/pdf";
import { RevenueChart } from "@/components/charts/RevenueChart";
import { ProfitChart } from "@/components/charts/ProfitChart";
import {
  AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Cell, PieChart, Pie, Legend,
} from "recharts";

function downloadCSV(filename: string, headers: string[], rows: (string | number)[][]) {
  const escape = (v: string | number) => `"${String(v).replace(/"/g, '""')}"`;
  const csv = [headers, ...rows].map((r) => r.map(escape).join(",")).join("\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

const PERIODS = [
  { value: "7d", label: "7 Days" },
  { value: "30d", label: "30 Days" },
  { value: "90d", label: "90 Days" },
  { value: "1y", label: "1 Year" },
];

export default function AnalyticsPage() {
  const [period, setPeriod] = useState("30d");
  const [tab, setTab] = useState<"overview" | "products" | "platforms">("overview");

  const { data: overview } = useQuery({
    queryKey: ["analytics-overview", period],
    queryFn: () => api.getAnalytics(period),
    placeholderData: SAMPLE_OVERVIEW,
  });

  const data = (overview as any) ?? SAMPLE_OVERVIEW;

  return (
    <div className="p-6 max-w-[1600px] mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <BarChart3 className="w-5 h-5 text-violet-400" />
            <h1 className="text-xl font-bold text-white">Analytics</h1>
          </div>
          <p className="text-sm text-white/40">Revenue · Profit · Units · ACoS · Platform breakdown</p>
        </div>
        <div className="flex gap-1 bg-white/5 rounded-lg p-1">
          {PERIODS.map((p) => (
            <button key={p.value} onClick={() => setPeriod(p.value)}
              className={cn("px-3 py-1.5 rounded-md text-xs font-medium transition-all",
                period === p.value ? "bg-violet-600 text-white" : "text-white/40 hover:text-white")}>
              {p.label}
            </button>
          ))}
        </div>
      </div>

      {/* KPI row */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
        {[
          { label: "Revenue", value: formatCurrency(data.revenue ?? 48500), change: data.revenue_change ?? 14.6, icon: DollarSign },
          { label: "Net Profit", value: formatCurrency(data.profit ?? 12800), change: data.profit_change ?? 8.2, icon: TrendingUp },
          { label: "Units Sold", value: formatNumber(data.units_sold ?? 1620), change: 11.3, icon: ShoppingCart },
          { label: "ACoS", value: `${data.acos ?? 18.4}%`, change: -2.1, icon: Target, invertChange: true },
          { label: "Profit Margin", value: `${data.margin_percent ?? (data.revenue > 0 ? ((data.profit / data.revenue) * 100).toFixed(1) : 0)}%`, change: 1.8, icon: BarChart3 },
        ].map((kpi) => {
          const Icon = kpi.icon;
          const isPositive = (kpi.invertChange ? -1 : 1) * kpi.change >= 0;
          return (
            <div key={kpi.label} className="bg-[#111218] border border-white/5 rounded-xl p-4">
              <div className="flex items-center justify-between mb-3">
                <Icon className="w-4 h-4 text-white/30" />
                <span className={cn("text-xs font-medium px-1.5 py-0.5 rounded-full",
                  isPositive ? "text-emerald-400 bg-emerald-500/15" : "text-red-400 bg-red-500/15")}>
                  {kpi.change >= 0 ? "+" : ""}{kpi.change}%
                </span>
              </div>
              <p className="text-xl font-bold text-white">{kpi.value}</p>
              <p className="text-xs text-white/40 mt-1">{kpi.label}</p>
            </div>
          );
        })}
      </div>

      {/* Tabs */}
      <div className="flex gap-1 mb-5 bg-white/5 rounded-lg p-1 w-fit">
        {[{ id: "overview", label: "Overview" }, { id: "products", label: "By Product" }, { id: "platforms", label: "By Platform" }]
          .map((t) => (
            <button key={t.id} onClick={() => setTab(t.id as any)}
              className={cn("px-4 py-1.5 rounded-md text-xs font-medium transition-all",
                tab === t.id ? "bg-violet-600 text-white" : "text-white/40 hover:text-white")}>
              {t.label}
            </button>
          ))}
      </div>

      {tab === "overview" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
          <div className="lg:col-span-2 bg-[#111218] border border-white/5 rounded-xl p-5">
            <p className="text-sm font-semibold text-white mb-4">Revenue vs Profit</p>
            <RevenueChart />
          </div>
          <div className="bg-[#111218] border border-white/5 rounded-xl p-5">
            <p className="text-sm font-semibold text-white mb-4">Profit by Platform</p>
            <ProfitChart />
          </div>
          <div className="lg:col-span-2 bg-[#111218] border border-white/5 rounded-xl p-5">
            <p className="text-sm font-semibold text-white mb-4">Profit Breakdown</p>
            <ProfitBreakdownChart data={data} />
          </div>
          <div className="bg-[#111218] border border-white/5 rounded-xl p-5">
            <p className="text-sm font-semibold text-white mb-4">Revenue Mix</p>
            <PlatformPieChart />
          </div>
        </div>
      )}

      {tab === "products" && <TopProductsTable period={period} />}
      {tab === "platforms" && <PlatformBreakdown />}
    </div>
  );
}

function ProfitBreakdownChart({ data }: { data: any }) {
  const chartData = [
    { name: "Gross Revenue", value: data.revenue ?? 48500, fill: "#8B5CF6" },
    { name: "COGS", value: -(data.revenue ?? 48500) * 0.3, fill: "#EF4444" },
    { name: "Platform Fees", value: -(data.revenue ?? 48500) * 0.18, fill: "#F59E0B" },
    { name: "Ad Spend", value: -(data.revenue ?? 48500) * 0.12, fill: "#EC4899" },
    { name: "Net Profit", value: data.profit ?? 12800, fill: "#10B981" },
  ];
  return (
    <ResponsiveContainer width="100%" height={200}>
      <BarChart data={chartData} layout="vertical" margin={{ left: 80 }}>
        <XAxis type="number" tick={{ fontSize: 10, fill: "rgba(255,255,255,0.3)" }} tickLine={false} axisLine={false}
          tickFormatter={(v) => `$${Math.abs(v / 1000).toFixed(0)}k`} />
        <YAxis dataKey="name" type="category" tick={{ fontSize: 10, fill: "rgba(255,255,255,0.5)" }} tickLine={false} axisLine={false} width={80} />
        <Tooltip contentStyle={{ background: "#1A1B22", border: "1px solid rgba(255,255,255,0.1)", borderRadius: "8px" }}
          formatter={(v: number) => [formatCurrency(Math.abs(v)), ""]} />
        <Bar dataKey="value" radius={[0, 4, 4, 0]}>
          {chartData.map((entry, i) => <Cell key={i} fill={entry.fill} fillOpacity={0.85} />)}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

const PLATFORM_COLORS: Record<string, string> = {
  amazon: "#F59E0B", walmart: "#3B82F6", shopify: "#8B5CF6", ebay: "#10B981", tiktok: "#EC4899",
};

function PlatformPieChart() {
  const { data: rawData } = useQuery({
    queryKey: ["by-platform-pie"],
    queryFn: () => api.getByPlatform("30d"),
    staleTime: 1000 * 60 * 5,
  });
  const data = (rawData ?? []).map((r: any) => ({
    name: r.marketplace.charAt(0).toUpperCase() + r.marketplace.slice(1),
    value: Math.round(r.profit),
    color: PLATFORM_COLORS[r.marketplace.toLowerCase()] ?? "#6B7280",
  }));
  return (
    <ResponsiveContainer width="100%" height={200}>
      <PieChart>
        <Pie data={data} cx="50%" cy="50%" innerRadius={55} outerRadius={80} paddingAngle={3} dataKey="value">
          {data.map((entry: any, i: number) => <Cell key={i} fill={entry.color} />)}
        </Pie>
        <Tooltip formatter={(v: number) => [formatCurrency(v), "Profit"]}
          contentStyle={{ background: "#1A1B22", border: "1px solid rgba(255,255,255,0.1)", borderRadius: "8px" }} />
        <Legend iconSize={8} iconType="circle" formatter={(v) => <span style={{ color: "rgba(255,255,255,0.5)", fontSize: 11 }}>{v}</span>} />
      </PieChart>
    </ResponsiveContainer>
  );
}

function TopProductsTable({ period }: { period: string }) {
  const { data: rows, isLoading } = useQuery({
    queryKey: ["by-product", period],
    queryFn: () => api.getByProduct(period, 10, "revenue"),
    staleTime: 1000 * 60 * 5,
  });

  const { data: productList } = useQuery({
    queryKey: ["products-for-analytics"],
    queryFn: () => api.listProducts({ limit: 100 }),
    staleTime: 1000 * 60 * 10,
  });

  const productTitles: Record<string, string> = {};
  const productItems: any[] = Array.isArray(productList) ? productList :
    (productList as any)?.items ?? [];
  productItems.forEach((p: any) => {
    productTitles[p.id] = p.title ?? p.name ?? "";
  });

  const products = rows ?? [];

  const handleExport = () => {
    if (products.length === 0) return;
    downloadCSV(
      `analytics-by-product-${period}.csv`,
      ["Product", "Product ID", "Revenue", "Profit", "Units", "Margin %"],
      (products as any[]).map((p: any) => {
        const name = p.product_title ?? p.product_name ?? productTitles[p.product_id] ?? p.product_id;
        const margin = p.revenue > 0 ? ((p.profit / p.revenue) * 100).toFixed(1) : "0";
        return [name, p.product_id, p.revenue, p.profit, p.units, margin];
      })
    );
  };

  const handleExportPDF = async () => {
    if (products.length === 0) return;
    const totalRevenue = (products as any[]).reduce((s: number, p: any) => s + (p.revenue ?? 0), 0);
    const totalProfit  = (products as any[]).reduce((s: number, p: any) => s + (p.profit  ?? 0), 0);
    await downloadPDF({
      title: "Analytics — By Product",
      subtitle: `Period: ${period} · ${(products as any[]).length} products`,
      filename: `analytics-by-product-${period}.pdf`,
      summaryRows: [
        { label: "Total Revenue", value: formatCurrency(totalRevenue) },
        { label: "Total Profit",  value: formatCurrency(totalProfit)  },
        { label: "Products",      value: String((products as any[]).length) },
        { label: "Avg Margin",    value: totalRevenue > 0 ? `${((totalProfit / totalRevenue) * 100).toFixed(1)}%` : "—" },
      ],
      columns: [
        { header: "Product",   key: "name",    width: 2.8, align: "left" },
        { header: "Revenue",   key: "revenue", width: 1,   align: "right", format: (v) => formatCurrency(v) },
        { header: "Profit",    key: "profit",  width: 1,   align: "right", format: (v) => formatCurrency(v), color: (v) => v >= 0 ? [16, 185, 129] : [239, 68, 68] },
        { header: "Units",     key: "units",   width: 0.7, align: "right" },
        { header: "Margin %",  key: "margin",  width: 0.8, align: "right", format: (v) => `${v}%` },
      ],
      rows: (products as any[]).map((p: any) => ({
        name:    p.product_title ?? p.product_name ?? productTitles[p.product_id] ?? p.product_id,
        revenue: p.revenue ?? 0,
        profit:  p.profit  ?? 0,
        units:   p.units   ?? 0,
        margin:  p.revenue > 0 ? ((p.profit / p.revenue) * 100).toFixed(1) : "0",
      })),
    });
  };

  return (
    <div className="bg-[#111218] border border-white/5 rounded-xl overflow-hidden">
      <div className="relative px-4 py-2.5 border-b border-white/5">
        <div className="grid grid-cols-5 text-[10px] font-semibold uppercase text-white/25">
          <span className="col-span-2">Product</span>
          <span>Revenue</span>
          <span>Profit</span>
          <span>Units</span>
        </div>
        {products.length > 0 && (
          <div className="absolute right-4 top-1/2 -translate-y-1/2 flex items-center gap-3">
            <button onClick={handleExportPDF} className="flex items-center gap-1 text-[10px] text-white/30 hover:text-red-400 transition-colors">
              <FileText className="w-3 h-3" />
              PDF
            </button>
            <button onClick={handleExport} className="flex items-center gap-1 text-[10px] text-white/30 hover:text-violet-400 transition-colors">
              <Download className="w-3 h-3" />
              CSV
            </button>
          </div>
        )}
      </div>
      {isLoading ? (
        <div className="px-4 py-8 text-center text-xs text-white/20">Loading…</div>
      ) : products.length === 0 ? (
        <div className="px-4 py-8 text-center text-xs text-white/20">No data for this period</div>
      ) : (
        products.map((p: any, i: number) => {
          const displayName = p.product_title ?? p.product_name ??
            productTitles[p.product_id] ?? null;
          return (
            <div key={i} className="grid grid-cols-5 px-4 py-3 border-b border-white/3 hover:bg-white/3 items-center">
              <div className="col-span-2 min-w-0">
                <p className="text-sm text-white font-medium truncate">
                  {displayName ?? `Product ${i + 1}`}
                </p>
                <p className="text-[10px] text-white/30 font-mono">
                  {p.product_id?.slice(0, 8)}…
                </p>
              </div>
              <span className="text-sm text-white">{formatCurrency(p.revenue)}</span>
              <span className="text-sm text-emerald-400">{formatCurrency(p.profit)}</span>
              <span className="text-sm text-white/60">{p.units}</span>
            </div>
          );
        })
      )}
    </div>
  );
}

function PlatformBreakdown() {
  const { data: rawData, isLoading } = useQuery({
    queryKey: ["by-platform-breakdown"],
    queryFn: () => api.getByPlatform("30d"),
    staleTime: 1000 * 60 * 5,
  });
  const ICONS: Record<string, string> = { amazon: "🛒", walmart: "🏪", shopify: "🛍️", ebay: "🏷️", tiktok: "📱" };
  const platforms = (rawData ?? []).map((r: any) => ({
    name: r.marketplace.charAt(0).toUpperCase() + r.marketplace.slice(1),
    revenue: r.revenue,
    profit: r.profit,
    orders: r.orders,
    icon: ICONS[r.marketplace.toLowerCase()] ?? "🌐",
  }));

  if (isLoading) return <div className="text-xs text-white/20 py-8 text-center">Loading…</div>;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
      {platforms.map((p: any) => (
        <div key={p.name} className="bg-[#111218] border border-white/5 rounded-xl p-5">
          <div className="flex items-center gap-2 mb-4">
            <span className="text-xl">{p.icon}</span>
            <span className="text-sm font-semibold text-white">{p.name}</span>
          </div>
          <div className="grid grid-cols-2 gap-3">
            {[
              { label: "Revenue", value: formatCurrency(p.revenue) },
              { label: "Profit", value: formatCurrency(p.profit) },
              { label: "Orders", value: String(p.orders) },
            ].map((s) => (
              <div key={s.label}>
                <p className="text-[10px] text-white/30">{s.label}</p>
                <p className="text-sm font-semibold text-white">{s.value}</p>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

const SAMPLE_OVERVIEW = { revenue: 0, revenue_change: 0, profit: 0, profit_change: 0, units_sold: 0, orders: 0, acos: 0, margin_percent: 0 };
