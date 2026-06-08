"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Package, AlertTriangle, CheckCircle2, TrendingDown, RefreshCw, ShoppingCart, BarChart3, Download, FileText } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useQuery, useMutation } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { toast } from "sonner";
import { cn, formatCurrency, formatNumber } from "@/lib/utils";
import { downloadPDF } from "@/lib/pdf";

function downloadCSV(filename: string, headers: string[], rows: (string | number)[][]) {
  const escape = (v: string | number) => `"${String(v).replace(/"/g, '""')}"`;
  const csv = [headers, ...rows].map((r) => r.map(escape).join(",")).join("\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = filename; a.click();
  URL.revokeObjectURL(url);
}

export default function InventoryPage() {
  const [tab, setTab] = useState<"overview" | "reorder" | "overstock">("overview");
  const { data: stockouts, isLoading } = useQuery({
    queryKey: ["stockout-predictions"],
    queryFn: () => api.getStockoutPredictions(),
  });
  const { data: inventoryItems } = useQuery({
    queryKey: ["inventory-items"],
    queryFn: () => api.getInventory(),
    staleTime: 1000 * 60 * 5,
  });
  const syncMutation = useMutation({
    mutationFn: () => api.syncInventory(),
    onSuccess: () => toast.success("Inventory synced successfully"),
    onError: () => toast.error("Sync failed — check your marketplace connection"),
  });

  const predictions = (stockouts as any[]) ?? SAMPLE_PREDICTIONS;
  const allInventory: any[] = Array.isArray(inventoryItems) ? inventoryItems :
    (inventoryItems as any)?.items ?? predictions;

  const criticalCount = predictions.filter((p: any) => p.urgency === "critical").length;
  const warningCount = predictions.filter((p: any) => p.urgency === "warning").length;
  const totalSKUs = allInventory.length || predictions.length;
  const avgDays = allInventory.length > 0
    ? Math.round(allInventory.reduce((s: number, p: any) => s + (p.days_remaining ?? 38), 0) / allInventory.length)
    : predictions.length > 0
    ? Math.round(predictions.reduce((s: number, p: any) => s + (p.days_remaining ?? 38), 0) / predictions.length)
    : 38;

  return (
    <div className="p-6 max-w-[1400px] mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Package className="w-5 h-5 text-blue-400" />
            <h1 className="text-xl font-bold text-white">Inventory Command Center</h1>
            <Badge className="bg-blue-500/20 text-blue-400 border-0 text-xs">Module 11</Badge>
          </div>
          <p className="text-sm text-white/40">Predict stockouts · Auto reorder plans · Overstock analysis</p>
        </div>
        <Button onClick={() => syncMutation.mutate()}
          disabled={syncMutation.isPending}
          variant="outline" size="sm"
          className="border-white/10 bg-white/5 text-white/60 hover:text-white">
          <RefreshCw className={cn("w-3.5 h-3.5 mr-1.5", syncMutation.isPending && "animate-spin")} />
          Sync All Platforms
        </Button>
      </div>

      {/* Alert banners */}
      {criticalCount > 0 && (
        <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }}
          className="bg-red-500/10 border border-red-500/30 rounded-xl px-4 py-3 mb-5 flex items-center gap-3">
          <AlertTriangle className="w-4 h-4 text-red-400 flex-shrink-0" />
          <p className="text-sm text-red-300">
            <strong>{criticalCount} product{criticalCount > 1 ? "s" : ""}</strong> will stock out in under 14 days.
            Immediate reorder required.
          </p>
          <Button size="sm" className="ml-auto bg-red-600 hover:bg-red-500 h-7 text-xs">
            View Reorder Plan
          </Button>
        </motion.div>
      )}

      {/* KPI cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        {[
          { label: "Total SKUs", value: totalSKUs.toString(), icon: Package, color: "blue" },
          { label: "Critical Stockout", value: criticalCount.toString(), icon: AlertTriangle, color: "red" },
          { label: "Reorder Needed", value: warningCount.toString(), icon: ShoppingCart, color: "amber" },
          { label: "Avg Days of Stock", value: `${avgDays}d`, icon: BarChart3, color: "emerald" },
        ].map((kpi) => {
          const Icon = kpi.icon;
          const colors = { blue: "text-blue-400 bg-blue-500/10", red: "text-red-400 bg-red-500/10",
            amber: "text-amber-400 bg-amber-500/10", emerald: "text-emerald-400 bg-emerald-500/10" };
          const [textColor, bgColor] = (colors[kpi.color as keyof typeof colors] || "").split(" ");
          return (
            <div key={kpi.label} className="bg-[#111218] border border-white/5 rounded-xl p-4">
              <div className={cn("w-8 h-8 rounded-lg flex items-center justify-center mb-3", bgColor)}>
                <Icon className={cn("w-4 h-4", textColor)} />
              </div>
              <p className="text-2xl font-bold text-white">{kpi.value}</p>
              <p className="text-xs text-white/40">{kpi.label}</p>
            </div>
          );
        })}
      </div>

      {/* Tabs */}
      <div className="flex gap-1 mb-5 bg-white/5 rounded-lg p-1 w-fit">
        {[{ id: "overview", label: "All Inventory" }, { id: "reorder", label: "Reorder Plan" }, { id: "overstock", label: "Overstock" }]
          .map((t) => (
            <button key={t.id} onClick={() => setTab(t.id as any)}
              className={cn("px-4 py-1.5 rounded-md text-xs font-medium transition-all",
                tab === t.id ? "bg-blue-600 text-white" : "text-white/40 hover:text-white")}>
              {t.label}
            </button>
          ))}
      </div>

      {/* Inventory table */}
      {tab === "overview" && (
        <div className="bg-[#111218] border border-white/5 rounded-xl overflow-hidden">
          <div className="relative px-4 py-2.5 border-b border-white/5">
            <div className="grid grid-cols-7 text-[10px] font-semibold uppercase text-white/25 tracking-wide">
              <span className="col-span-2">Product</span>
              <span>On Hand</span>
              <span>Reserved</span>
              <span>Inbound</span>
              <span>Days Left</span>
              <span>Status</span>
            </div>
            {predictions.length > 0 && (
              <div className="absolute right-4 top-1/2 -translate-y-1/2 flex items-center gap-3">
                <button
                  onClick={async () => { await downloadPDF({
                    title: "Inventory Overview",
                    subtitle: `${predictions.length} SKUs · Generated ${new Date().toLocaleDateString()}`,
                    filename: "inventory-overview.pdf",
                    summaryRows: [
                      { label: "Total SKUs",    value: String(totalSKUs) },
                      { label: "Critical",      value: String(criticalCount) },
                      { label: "Low Stock",     value: String(warningCount) },
                      { label: "Avg Days Left", value: `${avgDays}d` },
                    ],
                    columns: [
                      { header: "Product",   key: "name",     width: 2.5, align: "left" },
                      { header: "SKU",       key: "sku",      width: 1.2, align: "left" },
                      { header: "On Hand",   key: "onHand",   width: 0.8, align: "right" },
                      { header: "Reserved",  key: "reserved", width: 0.8, align: "right" },
                      { header: "Inbound",   key: "inbound",  width: 0.8, align: "right" },
                      { header: "Days Left", key: "days",     width: 0.8, align: "right", color: (v) => v < 14 ? [239,68,68] : v < 30 ? [245,158,11] : null },
                      { header: "Status",    key: "status",   width: 1,   align: "left",  color: (v) => v === "critical" ? [239,68,68] : v === "warning" ? [245,158,11] : [16,185,129] },
                    ],
                    rows: predictions.map((p: any, i: number) => ({
                      name:     p.product_name ?? `Product ${String.fromCharCode(65 + i)}`,
                      sku:      p.sku ?? `SKU-00${i + 1}`,
                      onHand:   p.quantity_on_hand ?? 0,
                      reserved: p.reserved ?? 0,
                      inbound:  p.inbound ?? 0,
                      days:     p.days_remaining ?? 0,
                      status:   p.urgency === "critical" ? "critical" : p.urgency === "warning" ? "low stock" : "healthy",
                    })),
                  }); }}
                  className="flex items-center gap-1 text-[10px] text-white/30 hover:text-red-400 transition-colors"
                >
                  <FileText className="w-3 h-3" />
                  PDF
                </button>
                <button
                  onClick={() => downloadCSV(
                    "inventory-overview.csv",
                    ["Product", "SKU", "On Hand", "Reserved", "Inbound", "Days Left", "Status"],
                    predictions.map((p: any, i: number) => [
                      p.product_name ?? `Product ${String.fromCharCode(65 + i)}`,
                      p.sku ?? `SKU-00${i + 1}`,
                      p.quantity_on_hand ?? 0,
                      p.reserved ?? 0,
                      p.inbound ?? 0,
                      p.days_remaining ?? 0,
                      p.urgency ?? "healthy",
                    ])
                  )}
                  className="flex items-center gap-1 text-[10px] text-white/30 hover:text-blue-400 transition-colors"
                >
                  <Download className="w-3 h-3" />
                  CSV
                </button>
              </div>
            )}
          </div>
          {predictions.map((item: any, i: number) => (
            <motion.div key={i} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: i * 0.03 }}
              className="grid grid-cols-7 px-4 py-3 border-b border-white/3 hover:bg-white/3 items-center">
              <div className="col-span-2">
                <p className="text-sm text-white font-medium">{item.product_name ?? `Product ${String.fromCharCode(65 + i)}`}</p>
                <p className="text-[10px] text-white/30">{item.sku ?? `SKU-00${i + 1}`}</p>
              </div>
              <span className="text-sm text-white">{formatNumber(item.quantity_on_hand ?? 240)}</span>
              <span className="text-sm text-white/50">{formatNumber(item.reserved ?? 0)}</span>
              <span className="text-sm text-white/50 text-emerald-400">{formatNumber(item.inbound ?? 0)}</span>
              <span className={cn("text-sm font-semibold",
                item.days_remaining < 14 ? "text-red-400" :
                item.days_remaining < 30 ? "text-amber-400" : "text-white")}>
                {item.days_remaining ?? 38}d
              </span>
              <div>
                <Badge className={cn("border-0 text-[9px]",
                  item.urgency === "critical" ? "bg-red-500/20 text-red-400" :
                  item.urgency === "warning" ? "bg-amber-500/20 text-amber-400" :
                  "bg-emerald-500/20 text-emerald-400")}>
                  {item.urgency === "critical" ? "Critical" : item.urgency === "warning" ? "Low Stock" : "Healthy"}
                </Badge>
              </div>
            </motion.div>
          ))}
        </div>
      )}

      {tab === "reorder" && <ReorderPlan predictions={predictions} />}
    </div>
  );
}

function ReorderPlan({ predictions }: { predictions: any[] }) {
  const critical = predictions.filter((p) => p.urgency === "critical" || p.days_remaining < 30);
  return (
    <div className="space-y-3">
      {critical.map((item: any, i: number) => (
        <div key={i} className={cn("bg-[#111218] border rounded-xl p-4 flex items-center gap-4",
          item.urgency === "critical" ? "border-red-500/20" : "border-amber-500/20")}>
          <div className={cn("w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0",
            item.urgency === "critical" ? "bg-red-500/10" : "bg-amber-500/10")}>
            <AlertTriangle className={cn("w-5 h-5", item.urgency === "critical" ? "text-red-400" : "text-amber-400")} />
          </div>
          <div className="flex-1">
            <p className="text-sm font-semibold text-white">{item.product_name ?? "Product"}</p>
            <p className="text-xs text-white/40">
              {item.days_remaining ?? 10}d remaining · Reorder {item.reorder_units ?? 500} units by{" "}
              {item.order_by_date ?? "Jun 18, 2025"}
            </p>
          </div>
          <div className="text-right">
            <p className="text-sm font-bold text-white">
              {formatCurrency((item.reorder_units ?? 500) * 5.20)}
            </p>
            <p className="text-[10px] text-white/30">Est. cost</p>
          </div>
          <Button size="sm" className="bg-violet-600 hover:bg-violet-500 text-xs h-7">
            Create PO
          </Button>
        </div>
      ))}
    </div>
  );
}

const SAMPLE_PREDICTIONS = [
  { product_name: "Bamboo Cutting Board Set", sku: "BCB-001", quantity_on_hand: 42, reserved: 8, inbound: 0, days_remaining: 11, urgency: "critical", reorder_units: 500 },
  { product_name: "Silicone Kitchen Utensils", sku: "SKU-002", quantity_on_hand: 87, reserved: 12, inbound: 0, days_remaining: 22, urgency: "warning", reorder_units: 300 },
  { product_name: "Travel Coffee Mug", sku: "TCM-003", quantity_on_hand: 234, reserved: 45, inbound: 100, days_remaining: 52, urgency: "healthy" },
  { product_name: "Yoga Mat Premium", sku: "YMP-004", quantity_on_hand: 156, reserved: 20, inbound: 0, days_remaining: 38, urgency: "healthy" },
  { product_name: "LED Desk Lamp", sku: "LDL-005", quantity_on_hand: 63, reserved: 5, inbound: 200, days_remaining: 29, urgency: "warning" },
];
