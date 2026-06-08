"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Globe, CheckCircle2, XCircle, RefreshCw, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { formatDistanceToNow } from "date-fns";

const INTEGRATIONS_META: Record<string, { name: string; logo: string; description: string; scopes: string[]; oauthSupported: boolean }> = {
  amazon:     { name: "Amazon",       logo: "🛒", description: "Connect Amazon Seller Central via SP-API. Sync products, orders, inventory, and PPC.", scopes: ["Products", "Orders", "Inventory", "PPC", "Reports"], oauthSupported: true },
  walmart:    { name: "Walmart",      logo: "🏪", description: "Connect Walmart Marketplace. Sync listings, orders, and pricing.", scopes: ["Products", "Orders", "Pricing", "Inventory"], oauthSupported: false },
  shopify:    { name: "Shopify",      logo: "🛍️", description: "Connect your Shopify store. Sync products, orders, inventory, and analytics.", scopes: ["Products", "Orders", "Inventory", "Analytics"], oauthSupported: true },
  ebay:       { name: "eBay",         logo: "🔖", description: "Connect eBay seller account. Sync listings, orders, and buyer feedback.", scopes: ["Listings", "Orders", "Feedback"], oauthSupported: true },
  tiktok:     { name: "TikTok Shop",  logo: "🎵", description: "Connect TikTok Shop. Sync products, orders, and live shopping analytics.", scopes: ["Products", "Orders", "Live Analytics"], oauthSupported: true },
  etsy:       { name: "Etsy",         logo: "🌿", description: "Connect Etsy shop. Sync listings, orders, and shop stats.", scopes: ["Listings", "Orders", "Shop Stats"], oauthSupported: true },
  tiktok_shop:{ name: "TikTok Shop",  logo: "🎵", description: "Connect TikTok Shop. Sync products, orders, and live shopping analytics.", scopes: ["Products", "Orders", "Live Analytics"], oauthSupported: true },
};

const STATUS_CONFIG: Record<string, { label: string; color: string; icon: any }> = {
  connected: { label: "Connected", color: "text-emerald-400", icon: CheckCircle2 },
  pending:   { label: "Pending",   color: "text-amber-400",   icon: AlertCircle },
  error:     { label: "Error",     color: "text-red-400",      icon: AlertCircle },
  active:    { label: "Active",    color: "text-emerald-400", icon: CheckCircle2 },
};

export default function IntegrationsPage() {
  const [connecting, setConnecting] = useState<string | null>(null);

  const { data: integrations, isLoading } = useQuery({
    queryKey: ["integrations"],
    queryFn: () => api.getIntegrations(),
    staleTime: 1000 * 60 * 5,
  });

  const rows: any[] = Array.isArray(integrations) ? integrations : [];

  return (
    <div className="p-6 max-w-[1200px] mx-auto">
      <div className="flex items-center gap-2 mb-2">
        <Globe className="w-5 h-5 text-violet-400" />
        <h1 className="text-xl font-bold text-white">Marketplace Integrations</h1>
      </div>
      <p className="text-sm text-white/40 mb-6">
        Connect your selling accounts to sync data, manage listings, and enable AI automation.
      </p>

      {isLoading ? (
        <div className="flex items-center justify-center py-16 text-white/30">
          <RefreshCw className="w-5 h-5 animate-spin mr-2" />
          <span className="text-sm">Loading integrations…</span>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {rows.map((integration: any, i: number) => {
            const meta = INTEGRATIONS_META[integration.marketplace] ?? {
              name: integration.marketplace,
              logo: "🔗",
              description: `${integration.marketplace} marketplace integration.`,
              scopes: [],
              oauthSupported: false,
            };
            const isConnected = integration.connected;
            const status = integration.status;
            const statusCfg = STATUS_CONFIG[status ?? ""] ?? STATUS_CONFIG["pending"];
            const StatusIcon = statusCfg.icon;
            const isConnecting = connecting === integration.marketplace;
            const lastSync = integration.last_sync_at
              ? formatDistanceToNow(new Date(integration.last_sync_at), { addSuffix: true })
              : null;

            return (
              <motion.div
                key={integration.marketplace}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.04 }}
                className={cn(
                  "bg-[#111218] border rounded-xl p-5 transition-all",
                  isConnected ? "border-emerald-500/20" :
                  status === "error" ? "border-red-500/15" :
                  "border-white/5 hover:border-white/15"
                )}
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">{meta.logo}</span>
                    <div>
                      <p className="text-sm font-semibold text-white">{meta.name}</p>
                      <div className="flex items-center gap-1.5 mt-0.5">
                        <StatusIcon className={cn("w-3 h-3", statusCfg.color)} />
                        <span className={cn("text-[10px]", isConnected ? "text-emerald-400" : statusCfg.color)}>
                          {isConnected ? integration.account_name || "Connected" : statusCfg.label}
                        </span>
                      </div>
                    </div>
                  </div>
                  {isConnected && (
                    <Badge className="bg-emerald-500/20 text-emerald-400 border-0 text-[9px]">Active</Badge>
                  )}
                  {status === "error" && (
                    <Badge className="bg-red-500/20 text-red-400 border-0 text-[9px]">Error</Badge>
                  )}
                </div>

                <p className="text-xs text-white/40 leading-relaxed mb-3">{meta.description}</p>

                {lastSync && (
                  <p className="text-[10px] text-white/25 mb-3">Last sync: {lastSync}</p>
                )}

                <div className="flex flex-wrap gap-1 mb-4">
                  {meta.scopes.map((scope) => (
                    <span key={scope} className="text-[9px] bg-white/5 text-white/30 px-2 py-0.5 rounded-full">{scope}</span>
                  ))}
                </div>

                {!isConnected && isConnecting && !meta.oauthSupported && (
                  <div className="space-y-2 mb-3">
                    <input placeholder="Client ID"
                      className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-1.5 text-xs text-white placeholder:text-white/20 outline-none" />
                    <input placeholder="Client Secret" type="password"
                      className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-1.5 text-xs text-white placeholder:text-white/20 outline-none" />
                  </div>
                )}

                <div className="flex gap-2">
                  {isConnected ? (
                    <>
                      <Button size="sm" variant="outline" className="flex-1 h-7 text-xs border-white/10 bg-white/5 text-white/50 hover:text-white">
                        <RefreshCw className="w-3 h-3 mr-1" /> Sync Now
                      </Button>
                      <Button size="sm" variant="outline" className="h-7 text-xs border-red-500/20 text-red-400/70 hover:text-red-400 hover:bg-red-500/10">
                        Disconnect
                      </Button>
                    </>
                  ) : (
                    <Button
                      size="sm"
                      onClick={() => setConnecting(isConnecting ? null : integration.marketplace)}
                      className={cn(
                        "flex-1 h-7 text-xs",
                        meta.oauthSupported ? "bg-violet-600 hover:bg-violet-500" : "bg-white/10 hover:bg-white/15 text-white/60"
                      )}
                    >
                      {isConnecting ? "Cancel" : meta.oauthSupported ? "Connect with OAuth" : "Connect"}
                    </Button>
                  )}
                </div>
              </motion.div>
            );
          })}
        </div>
      )}
    </div>
  );
}
