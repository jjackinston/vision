"use client";

import { useState } from "react";
import { usePathname } from "next/navigation";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import { UserButton } from "@clerk/nextjs";
import {
  LayoutDashboard, Search, Target, TrendingUp, Package,
  FileText, BarChart3, Bot, Zap, ShoppingBag, Settings,
  ChevronLeft, Bell, Command, Brain, Warehouse, Users,
  DollarSign, Globe, Cpu, Lightbulb, Sparkles, X,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { CommandPalette } from "@/components/layout/CommandPalette";
import { NotificationPanel } from "@/components/layout/NotificationPanel";
import { VoiceAssistant } from "@/components/agents/VoiceAssistant";
import { ErrorBoundary } from "@/components/ui/error-boundary";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useWebSocket } from "@/hooks/useWebSocket";
import { useRealtimeEvents } from "@/hooks/useRealtimeEvents";

const navigation = [
  {
    section: "Intelligence",
    items: [
      { name: "AI CEO Dashboard", href: "/dashboard", icon: Brain, badge: "AI", badgeColor: "purple" },
      { name: "Product Research", href: "/products", icon: Search },
      { name: "Keyword Intelligence", href: "/keywords", icon: Target },
      { name: "Competitor Analysis", href: "/competitors", icon: TrendingUp },
      { name: "Trend Discovery", href: "/trends", icon: Lightbulb, badge: "Live" },
    ],
  },
  {
    section: "Operations",
    items: [
      { name: "Inventory Hub", href: "/inventory", icon: Package },
      { name: "Listing Manager", href: "/listings", icon: FileText },
      { name: "PPC Manager", href: "/ppc", icon: DollarSign },
      { name: "Suppliers", href: "/suppliers", icon: Warehouse },
    ],
  },
  {
    section: "Analytics",
    items: [
      { name: "Analytics", href: "/analytics", icon: BarChart3 },
      { name: "Profit Calculator", href: "/analytics/profit", icon: DollarSign },
      { name: "Digital Twin", href: "/analytics/twin", icon: Globe, badge: "Beta" },
    ],
  },
  {
    section: "AI Platform",
    items: [
      { name: "AI Agents", href: "/agents", icon: Bot, badge: "New" },
      { name: "Automation", href: "/automation", icon: Zap },
      { name: "Marketplace", href: "/marketplace", icon: ShoppingBag },
    ],
  },
  {
    section: "Account",
    items: [
      { name: "Team & Settings", href: "/settings", icon: Settings },
      { name: "Integrations", href: "/settings/integrations", icon: Cpu },
    ],
  },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const [collapsed, setCollapsed] = useState(false);
  const [commandOpen, setCommandOpen] = useState(false);
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const [trialDismissed, setTrialDismissed] = useState(false);
  const pathname = usePathname();

  // ── Real-time WebSocket events ──────────────────────────────────────────────
  const { handleRawMessage, unreadCount: wsUnreadCount, clearUnread } = useRealtimeEvents();

  // Fetch the current user's tenant_id so the WebSocket subscribes to the right channel
  const { data: meData } = useQuery({
    queryKey: ["me"],
    queryFn: () => api.getMe(),
    staleTime: Infinity, // user + tenant don't change during a session
    retry: false,        // dev: avoid noise if auth bypass returns nothing
  });

  // Derive WS URL from the API base URL (dev: http://localhost:8000 → ws://localhost:8000)
  const wsUrl = (() => {
    if (typeof window === "undefined") return null;
    const apiBase = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
    const tenantId = (meData as any)?.tenant_id ?? "11111111-1111-1111-1111-111111111111";
    return apiBase.replace(/^http/, "ws") + `/ws/${tenantId}`;
  })();

  useWebSocket(wsUrl, { onMessage: handleRawMessage });

  const { data: unreadData } = useQuery({
    queryKey: ["unread-count"],
    queryFn: () => api.getUnreadCount(),
    staleTime: 1000 * 60,
    refetchInterval: 1000 * 60,
  });
  // Merge polled count with live WS counter — whichever is higher wins
  const polledCount: number = (unreadData as any)?.count ?? 0;
  const unreadCount: number = polledCount + wsUnreadCount;

  const { data: subData } = useQuery({
    queryKey: ["subscription"],
    queryFn: () => api.getSubscription(),
    staleTime: 1000 * 60 * 5,
  });
  const sub: any = subData ?? {};
  const isTrialing = sub.status === "free_trial" || sub.status === "trialing";
  // trial_end is a unix timestamp from Stripe; free_trial has no end date so show 14 days from "now" as UX placeholder
  const trialDaysLeft = sub.trial_end
    ? Math.max(0, Math.ceil((sub.trial_end * 1000 - Date.now()) / 86_400_000))
    : 14;

  const handleUpgradeClick = async () => {
    try {
      const { checkout_url } = await api.createCheckoutSession("professional");
      window.location.href = checkout_url;
    } catch {
      window.location.href = "/settings";
    }
  };

  return (
    <TooltipProvider>
      <div className="flex h-screen bg-[#0A0B0E] text-white overflow-hidden">
        {/* Sidebar */}
        <motion.aside
          initial={false}
          animate={{ width: collapsed ? 68 : 240 }}
          transition={{ duration: 0.2, ease: "easeInOut" }}
          className="flex flex-col border-r border-white/5 bg-[#0D0E12] relative z-20"
        >
          {/* Logo */}
          <div className="flex items-center gap-3 px-4 py-5 border-b border-white/5">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-500 to-blue-500 flex items-center justify-center flex-shrink-0">
              <Brain className="w-4 h-4 text-white" />
            </div>
            {!collapsed && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="overflow-hidden">
                <p className="text-sm font-bold text-white leading-none">SellerVision</p>
                <p className="text-[10px] text-violet-400 font-medium">AI Platform</p>
              </motion.div>
            )}
          </div>

          {/* Navigation */}
          <nav className="flex-1 overflow-y-auto py-4 px-2 space-y-6">
            {navigation.map((section) => (
              <div key={section.section}>
                {!collapsed && (
                  <p className="px-2 mb-2 text-[10px] font-semibold uppercase tracking-widest text-white/30">
                    {section.section}
                  </p>
                )}
                <ul className="space-y-0.5">
                  {section.items.map((item) => {
                    const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
                    const Icon = item.icon;
                    return (
                      <li key={item.name}>
                        <Tooltip>
                          <TooltipTrigger asChild>
                            <Link
                              href={item.href}
                              className={cn(
                                "flex items-center gap-3 px-2 py-2 rounded-lg text-sm font-medium transition-all duration-150",
                                isActive
                                  ? "bg-violet-500/15 text-violet-300"
                                  : "text-white/50 hover:text-white hover:bg-white/5"
                              )}
                            >
                              <Icon className={cn("w-4 h-4 flex-shrink-0", isActive && "text-violet-400")} />
                              {!collapsed && (
                                <span className="flex-1 truncate">{item.name}</span>
                              )}
                              {!collapsed && item.badge && (
                                <Badge
                                  variant="outline"
                                  className={cn(
                                    "text-[9px] px-1.5 py-0 h-4 border-0",
                                    item.badgeColor === "purple"
                                      ? "bg-violet-500/20 text-violet-300"
                                      : "bg-emerald-500/20 text-emerald-400"
                                  )}
                                >
                                  {item.badge}
                                </Badge>
                              )}
                            </Link>
                          </TooltipTrigger>
                          {collapsed && (
                            <TooltipContent side="right">{item.name}</TooltipContent>
                          )}
                        </Tooltip>
                      </li>
                    );
                  })}
                </ul>
              </div>
            ))}
          </nav>

          {/* Collapse button */}
          <div className="p-3 border-t border-white/5">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setCollapsed(!collapsed)}
              className="w-full justify-center text-white/30 hover:text-white hover:bg-white/5 h-8"
            >
              <motion.div animate={{ rotate: collapsed ? 180 : 0 }}>
                <ChevronLeft className="w-4 h-4" />
              </motion.div>
            </Button>
          </div>
        </motion.aside>

        {/* Main */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Top bar */}
          <header className="h-14 border-b border-white/5 bg-[#0D0E12] flex items-center justify-between px-6 flex-shrink-0">
            <Button
              variant="ghost"
              onClick={() => setCommandOpen(true)}
              className="flex items-center gap-2 text-sm text-white/40 bg-white/5 rounded-lg px-4 h-8 hover:bg-white/10 hover:text-white/70 w-72"
            >
              <Command className="w-3.5 h-3.5" />
              <span>Search anything...</span>
              <kbd className="ml-auto text-[10px] bg-white/10 px-1.5 py-0.5 rounded">⌘K</kbd>
            </Button>

            <div className="flex items-center gap-3">
              <VoiceAssistant />
              <Button
                variant="ghost"
                size="icon"
                onClick={() => { setNotificationsOpen(true); clearUnread(); }}
                className="relative text-white/40 hover:text-white hover:bg-white/5 h-8 w-8"
              >
                <Bell className="w-4 h-4" />
                {unreadCount > 0 && (
                  <span className="absolute top-1 right-1 w-2 h-2 bg-violet-500 rounded-full" />
                )}
              </Button>
              {process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY && (
                <UserButton afterSignOutUrl="/login" />
              )}
            </div>
          </header>

          {/* Trial banner */}
          <AnimatePresence>
            {isTrialing && !trialDismissed && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: "auto", opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.2 }}
                className="overflow-hidden flex-shrink-0"
              >
                <div className="bg-gradient-to-r from-violet-600/90 to-blue-600/90 px-6 py-2 flex items-center justify-between">
                  <div className="flex items-center gap-2 text-white text-sm">
                    <Sparkles className="w-3.5 h-3.5 text-yellow-300 flex-shrink-0" />
                    <span>
                      <strong>{trialDaysLeft} day{trialDaysLeft !== 1 ? "s" : ""}</strong> left on your free trial.
                      Upgrade to unlock all 23 modules and unlimited usage.
                    </span>
                  </div>
                  <div className="flex items-center gap-3 flex-shrink-0 ml-4">
                    <button
                      onClick={handleUpgradeClick}
                      className="bg-white text-violet-700 font-semibold text-xs px-3 py-1 rounded-full hover:bg-white/90 transition-colors"
                    >
                      Upgrade Now
                    </button>
                    <button
                      onClick={() => setTrialDismissed(true)}
                      className="text-white/60 hover:text-white transition-colors"
                      aria-label="Dismiss"
                    >
                      <X className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Page content */}
          <main className="flex-1 overflow-auto bg-[#0A0B0E]">
            <AnimatePresence mode="wait">
              <motion.div
                key={pathname}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                transition={{ duration: 0.15 }}
                className="h-full"
              >
                <ErrorBoundary>
                  {children}
                </ErrorBoundary>
              </motion.div>
            </AnimatePresence>
          </main>
        </div>

        {/* Overlays */}
        <CommandPalette open={commandOpen} onClose={() => setCommandOpen(false)} />
        <NotificationPanel open={notificationsOpen} onClose={() => setNotificationsOpen(false)} />
      </div>
    </TooltipProvider>
  );
}
