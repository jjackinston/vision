"use client";

import { motion, AnimatePresence } from "framer-motion";
import { X, Bell, AlertTriangle, TrendingUp, Package, DollarSign, Star, CheckCircle2, Bot, RefreshCw, ExternalLink } from "lucide-react";
import { cn } from "@/lib/utils";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { formatDistanceToNow } from "date-fns";

const TYPE_CONFIG: Record<string, { bg: string; border: string; dot: string; icon: any }> = {
  stockout_alert:   { bg: "bg-red-500/10",     border: "border-red-500/20",     dot: "bg-red-500",     icon: Package },
  trend_alert:      { bg: "bg-violet-500/10",  border: "border-violet-500/20",  dot: "bg-violet-500",  icon: TrendingUp },
  ppc_alert:        { bg: "bg-amber-500/10",   border: "border-amber-500/20",   dot: "bg-amber-500",   icon: DollarSign },
  competitor_alert: { bg: "bg-orange-500/10",  border: "border-orange-500/20",  dot: "bg-orange-500",  icon: TrendingUp },
  milestone:        { bg: "bg-emerald-500/10", border: "border-emerald-500/20", dot: "bg-emerald-500", icon: Star },
  listing_alert:    { bg: "bg-blue-500/10",    border: "border-blue-500/20",    dot: "bg-blue-500",    icon: CheckCircle2 },
  agent_complete:   { bg: "bg-violet-500/10",  border: "border-violet-500/20",  dot: "bg-violet-500",  icon: Bot },
  supplier_alert:   { bg: "bg-emerald-500/10", border: "border-emerald-500/20", dot: "bg-emerald-500", icon: Package },
  system:           { bg: "bg-white/5",        border: "border-white/10",       dot: "bg-white/40",    icon: Bell },
  critical:         { bg: "bg-red-500/10",     border: "border-red-500/20",     dot: "bg-red-500",     icon: AlertTriangle },
  warning:          { bg: "bg-amber-500/10",   border: "border-amber-500/20",   dot: "bg-amber-500",   icon: AlertTriangle },
  opportunity:      { bg: "bg-emerald-500/10", border: "border-emerald-500/20", dot: "bg-emerald-500", icon: TrendingUp },
  info:             { bg: "bg-violet-500/10",  border: "border-violet-500/20",  dot: "bg-violet-500",  icon: Bell },
};

const DEFAULT_CONFIG = { bg: "bg-white/5", border: "border-white/10", dot: "bg-white/30", icon: Bell };

interface NotificationPanelProps {
  open: boolean;
  onClose: () => void;
}

export function NotificationPanel({ open, onClose }: NotificationPanelProps) {
  const queryClient = useQueryClient();
  const router = useRouter();

  const { data: notifications, isLoading } = useQuery({
    queryKey: ["notifications"],
    queryFn: () => api.getNotifications({ limit: 30 }),
    staleTime: 1000 * 30,
    refetchInterval: open ? 1000 * 30 : false,
    enabled: open,
  });

  const markAllMutation = useMutation({
    mutationFn: () => api.markAllRead(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
      queryClient.invalidateQueries({ queryKey: ["unread-count"] });
    },
  });

  const markOneMutation = useMutation({
    mutationFn: (id: string) => api.markNotificationRead(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
      queryClient.invalidateQueries({ queryKey: ["unread-count"] });
    },
  });

  const rows: any[] = Array.isArray(notifications) ? notifications : [];
  const unreadCount = rows.filter((n: any) => !n.is_read).length;

  const handleNotificationClick = (n: any) => {
    if (!n.is_read) markOneMutation.mutate(n.id);
    if (n.action_url) {
      router.push(n.action_url);
      onClose();
    }
  };

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            onClick={onClose} className="fixed inset-0 z-40" />
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            className="fixed top-14 right-4 w-96 bg-[#13141A] border border-white/10 rounded-2xl shadow-2xl overflow-hidden z-50"
          >
            <div className="flex items-center justify-between px-4 py-3 border-b border-white/8">
              <div className="flex items-center gap-2">
                <Bell className="w-4 h-4 text-violet-400" />
                <span className="text-sm font-semibold text-white">Notifications</span>
                {unreadCount > 0 && (
                  <span className="text-[10px] bg-violet-500/20 text-violet-400 px-1.5 py-0.5 rounded-full">
                    {unreadCount}
                  </span>
                )}
              </div>
              <div className="flex items-center gap-2">
                {unreadCount > 0 && (
                  <button
                    onClick={() => markAllMutation.mutate()}
                    className="text-[11px] text-white/40 hover:text-violet-400 transition-colors"
                  >
                    Mark all read
                  </button>
                )}
                <button onClick={onClose} className="text-white/30 hover:text-white">
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>

            <div className="max-h-[480px] overflow-y-auto py-2">
              {isLoading ? (
                <div className="flex items-center justify-center py-10 text-white/30">
                  <RefreshCw className="w-4 h-4 animate-spin mr-2" />
                  <span className="text-xs">Loading…</span>
                </div>
              ) : rows.length === 0 ? (
                <div className="py-10 text-center">
                  <Bell className="w-8 h-8 text-white/10 mx-auto mb-2" />
                  <p className="text-xs text-white/30">No notifications yet</p>
                </div>
              ) : (
                rows.map((n: any) => {
                  const config = TYPE_CONFIG[n.type] ?? DEFAULT_CONFIG;
                  const Icon = config.icon;
                  const timeAgo = n.created_at
                    ? formatDistanceToNow(new Date(n.created_at), { addSuffix: true })
                    : "";
                  return (
                    <div
                      key={n.id}
                      onClick={() => handleNotificationClick(n)}
                      className={cn(
                        "mx-3 my-1.5 p-3 rounded-xl border transition-all",
                        config.bg, config.border,
                        n.is_read ? "opacity-50" : "hover:opacity-90",
                        (n.action_url || !n.is_read) ? "cursor-pointer" : "cursor-default"
                      )}
                    >
                      <div className="flex items-start gap-3">
                        <div className="w-7 h-7 rounded-lg bg-white/5 flex items-center justify-center flex-shrink-0">
                          <Icon className="w-3.5 h-3.5 text-white/50" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-0.5">
                            {!n.is_read && (
                              <div className={cn("w-1.5 h-1.5 rounded-full flex-shrink-0", config.dot)} />
                            )}
                            <p className={cn("text-xs font-semibold truncate flex-1", n.is_read ? "text-white/50" : "text-white")}>
                              {n.title}
                            </p>
                            {n.action_url && (
                              <ExternalLink className="w-3 h-3 text-white/25 flex-shrink-0" />
                            )}
                            <span className="text-[10px] text-white/25 flex-shrink-0">{timeAgo}</span>
                          </div>
                          {n.body && (
                            <p className="text-[11px] text-white/50 leading-relaxed">{n.body}</p>
                          )}
                          {n.action_url && !n.is_read && (
                            <p className="text-[10px] text-violet-400/70 mt-1">Click to view →</p>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })
              )}
            </div>

            <div className="px-4 py-3 border-t border-white/8">
              <button className="text-xs text-violet-400 hover:text-violet-300 w-full text-center">
                View all notifications
              </button>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
