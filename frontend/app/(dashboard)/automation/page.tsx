"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Zap, Play, Pause, Plus, Settings2, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { toast } from "sonner";
import { formatDistanceToNow } from "date-fns";

const CATEGORY_COLORS: Record<string, string> = {
  inventory: "bg-blue-500/20 text-blue-400",
  pricing: "bg-amber-500/20 text-amber-400",
  ppc: "bg-red-500/20 text-red-400",
  reviews: "bg-orange-500/20 text-orange-400",
  trends: "bg-violet-500/20 text-violet-400",
  reporting: "bg-emerald-500/20 text-emerald-400",
  schedule: "bg-sky-500/20 text-sky-400",
  event: "bg-purple-500/20 text-purple-400",
};

function inferCategory(wf: any): string {
  const name = (wf.name || "").toLowerCase();
  if (name.includes("inventory") || name.includes("stock") || name.includes("reorder")) return "inventory";
  if (name.includes("ppc") || name.includes("budget") || name.includes("bid")) return "ppc";
  if (name.includes("price") || name.includes("competitor")) return "pricing";
  if (name.includes("trend")) return "trends";
  if (name.includes("listing") || name.includes("seo")) return "reporting";
  if (name.includes("supplier")) return "inventory";
  return wf.trigger_type === "schedule" ? "schedule" : "event";
}

export default function AutomationPage() {
  const [tab, setTab] = useState<"workflows" | "templates" | "integrations">("workflows");
  const queryClient = useQueryClient();

  const { data: workflows, isLoading } = useQuery({
    queryKey: ["workflows"],
    queryFn: () => api.getWorkflows(),
    staleTime: 1000 * 60,
  });

  const { data: templates } = useQuery({
    queryKey: ["automation-templates"],
    queryFn: () => api.getAutomationTemplates(),
    staleTime: 1000 * 60 * 10,
  });

  const toggleMutation = useMutation({
    mutationFn: (id: string) => api.toggleWorkflow(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["workflows"] });
      toast.success("Workflow updated");
    },
    onError: () => toast.error("Failed to update workflow"),
  });

  const rows: any[] = Array.isArray(workflows) ? workflows : [];
  const templateRows: any[] = Array.isArray(templates) ? templates : [];
  const activeCount = rows.filter((w) => w.is_active).length;

  return (
    <div className="p-6 max-w-[1400px] mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Zap className="w-5 h-5 text-amber-400" />
            <h1 className="text-xl font-bold text-white">Automation Engine</h1>
            <Badge className="bg-amber-500/20 text-amber-400 border-0 text-xs">Module 22</Badge>
          </div>
          <p className="text-sm text-white/40">
            Build workflows · Connect Zapier, Make, n8n · Automate everything
            {rows.length > 0 && (
              <span className="ml-2 text-emerald-400">{activeCount}/{rows.length} active</span>
            )}
          </p>
        </div>
        <Button className="bg-amber-500 hover:bg-amber-400 text-black font-semibold text-sm">
          <Plus className="w-4 h-4 mr-1.5" />New Workflow
        </Button>
      </div>

      <div className="flex gap-1 mb-6 bg-white/5 rounded-lg p-1 w-fit">
        {[{ id: "workflows", label: "My Workflows" }, { id: "templates", label: "Templates" }, { id: "integrations", label: "Integrations" }]
          .map((t) => (
            <button key={t.id} onClick={() => setTab(t.id as any)}
              className={cn("px-4 py-1.5 rounded-md text-xs font-medium transition-all",
                tab === t.id ? "bg-amber-600 text-white" : "text-white/40 hover:text-white")}>
              {t.label}
            </button>
          ))}
      </div>

      {tab === "workflows" && (
        <div className="space-y-3">
          {isLoading ? (
            <div className="bg-[#111218] border border-white/5 rounded-xl p-8 text-center text-white/30">
              <RefreshCw className="w-5 h-5 animate-spin mx-auto mb-2" />
              <p className="text-sm">Loading workflows…</p>
            </div>
          ) : rows.length === 0 ? (
            <div className="bg-[#111218] border border-white/5 rounded-xl p-8 text-center text-white/30">
              <Zap className="w-8 h-8 mx-auto mb-2 opacity-30" />
              <p className="text-sm">No workflows yet — create one or use a template</p>
            </div>
          ) : (
            rows.map((wf: any, i: number) => {
              const category = inferCategory(wf);
              const lastRun = wf.last_run_at
                ? formatDistanceToNow(new Date(wf.last_run_at), { addSuffix: true })
                : "never";
              return (
                <motion.div key={wf.id} initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.05 }}
                  className="bg-[#111218] border border-white/5 rounded-xl p-4 flex items-center gap-4 hover:border-white/10 transition-all">
                  <div className={cn("w-8 h-8 rounded-lg flex items-center justify-center text-sm", CATEGORY_COLORS[category] || "bg-white/5 text-white/40")}>
                    <Zap className="w-4 h-4" />
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-semibold text-white">{wf.name}</p>
                    <p className="text-xs text-white/30">
                      Last run: {lastRun}
                      {wf.run_count != null && ` · ${wf.run_count} total runs`}
                    </p>
                  </div>
                  <Badge className={cn("border-0 text-[10px] capitalize", CATEGORY_COLORS[category] || "bg-white/5 text-white/30")}>
                    {wf.trigger_type || category}
                  </Badge>
                  <div className="flex items-center gap-2">
                    <div className={cn("w-2 h-2 rounded-full", wf.is_active ? "bg-emerald-500 animate-pulse" : "bg-white/20")} />
                    <span className={cn("text-xs", wf.is_active ? "text-emerald-400" : "text-white/30")}>
                      {wf.is_active ? "active" : "paused"}
                    </span>
                  </div>
                  <div className="flex gap-1.5">
                    <Button
                      size="sm" variant="ghost"
                      className="h-7 px-2 text-white/30 hover:text-white"
                      onClick={() => toggleMutation.mutate(wf.id)}
                      disabled={toggleMutation.isPending && toggleMutation.variables === wf.id}
                    >
                      {wf.is_active ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
                    </Button>
                    <Button size="sm" variant="ghost" className="h-7 px-2 text-white/30 hover:text-white">
                      <Settings2 className="w-3.5 h-3.5" />
                    </Button>
                  </div>
                </motion.div>
              );
            })
          )}
        </div>
      )}

      {tab === "templates" && (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {templateRows.map((tmpl: any, i: number) => {
            const category = tmpl.category || "schedule";
            const ICONS: Record<string, string> = {
              inventory: "📦", pricing: "💰", ppc: "📊", reviews: "⭐", trends: "🚀", reporting: "📋",
            };
            return (
              <motion.div key={tmpl.id} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.04 }}
                className="bg-[#111218] border border-white/5 rounded-xl p-5 hover:border-white/15 transition-all">
                <div className="flex items-center gap-3 mb-3">
                  <span className="text-2xl">{ICONS[category] || "⚙️"}</span>
                  <div>
                    <p className="text-sm font-semibold text-white">{tmpl.name}</p>
                    <Badge className={cn("border-0 text-[10px] capitalize", CATEGORY_COLORS[category] || "bg-white/5 text-white/30")}>{category}</Badge>
                  </div>
                </div>
                <p className="text-xs text-white/40 mb-3">
                  <span className="text-white/30">Trigger:</span> {tmpl.trigger || "—"}
                </p>
                <p className="text-xs text-white/30 mb-4">{(tmpl.steps || []).length} automation steps</p>
                <Button size="sm" className="w-full h-7 text-xs bg-white/10 hover:bg-white/15 text-white/70">
                  <Plus className="w-3 h-3 mr-1" />Use Template
                </Button>
              </motion.div>
            );
          })}
        </div>
      )}

      {tab === "integrations" && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {[
            { name: "Zapier", logo: "⚡", description: "Connect to 6,000+ apps via Zapier triggers and actions.", status: "available" },
            { name: "Make (Integromat)", logo: "🔄", description: "Visual automation builder with advanced data transformation.", status: "available" },
            { name: "n8n", logo: "🔗", description: "Self-hosted workflow automation. Full API access.", status: "available" },
            { name: "Webhooks", logo: "📡", description: "Send real-time events to any URL when triggers fire.", status: "available" },
            { name: "Slack", logo: "💬", description: "Send alerts and reports to Slack channels.", status: "available" },
            { name: "Email (SendGrid)", logo: "📧", description: "Trigger email alerts, reports, and notifications.", status: "coming" },
          ].map((intg) => (
            <div key={intg.name} className={cn("bg-[#111218] border rounded-xl p-5", intg.status === "coming" ? "border-white/5 opacity-60" : "border-white/5 hover:border-white/15")} >
              <div className="flex items-center gap-3 mb-3">
                <span className="text-2xl">{intg.logo}</span>
                <div>
                  <p className="text-sm font-semibold text-white">{intg.name}</p>
                  {intg.status === "coming" && <Badge className="bg-white/5 text-white/30 border-0 text-[9px]">Coming Soon</Badge>}
                </div>
              </div>
              <p className="text-xs text-white/40 mb-4">{intg.description}</p>
              <Button size="sm" disabled={intg.status === "coming"}
                className="w-full h-7 text-xs bg-white/8 hover:bg-white/15 text-white/60">
                {intg.status === "coming" ? "Coming Soon" : "Connect"}
              </Button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
