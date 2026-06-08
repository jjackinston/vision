"use client";

import React, { useEffect, useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useRouter } from "next/navigation";
import {
  Search, Brain, Package, Target, TrendingUp, BarChart3,
  Bot, FileText, Zap, Settings, ArrowRight, Tag, DollarSign,
  Warehouse, Globe, ShoppingBag, Lightbulb,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

type CommandItem = {
  label: string;
  icon: React.ElementType;
  href?: string;
  shortcut?: string;
  action?: string;
  subtitle?: string;
};

const STATIC_COMMANDS: { group: string; items: CommandItem[] }[] = [
  {
    group: "Navigate",
    items: [
      { label: "AI CEO Dashboard",     icon: Brain,       href: "/dashboard",        shortcut: "G D" },
      { label: "Product Research",     icon: Search,      href: "/products",         shortcut: "G P" },
      { label: "Keyword Intelligence", icon: Target,      href: "/keywords",         shortcut: "G K" },
      { label: "Competitor Analysis",  icon: TrendingUp,  href: "/competitors" },
      { label: "Analytics",            icon: BarChart3,   href: "/analytics" },
      { label: "Profit Calculator",    icon: DollarSign,  href: "/analytics/profit" },
      { label: "Digital Twin",         icon: Globe,       href: "/analytics/twin" },
      { label: "AI Agents",            icon: Bot,         href: "/agents" },
      { label: "Inventory Hub",        icon: Package,     href: "/inventory" },
      { label: "Listings Manager",     icon: FileText,    href: "/listings" },
      { label: "PPC Manager",          icon: DollarSign,  href: "/ppc" },
      { label: "Suppliers",            icon: Warehouse,   href: "/suppliers" },
      { label: "Trend Discovery",      icon: Lightbulb,   href: "/trends" },
      { label: "Automation",           icon: Zap,         href: "/automation" },
      { label: "Marketplace",          icon: ShoppingBag, href: "/marketplace" },
      { label: "Settings",             icon: Settings,    href: "/settings" },
    ],
  },
  {
    group: "Quick Actions",
    items: [
      { label: "Track a new product",          icon: Package,   href: "/products",        action: "track-product" },
      { label: "Run AI opportunity scan",      icon: Brain,     href: "/products",        action: "opportunity-scan" },
      { label: "Generate listing for product", icon: FileText,  href: "/listings",        action: "generate-listing" },
      { label: "Simulate business scenario",   icon: BarChart3, href: "/analytics/twin",  action: "digital-twin" },
      { label: "Analyze competitor weakness",  icon: TrendingUp,href: "/competitors",     action: "competitor-scan" },
      { label: "View keyword opportunities",   icon: Target,    href: "/keywords",        action: "keyword-opps" },
    ],
  },
];

interface CommandPaletteProps {
  open: boolean;
  onClose: () => void;
}

export function CommandPalette({ open, onClose }: CommandPaletteProps) {
  const [query, setQuery] = useState("");
  const [focusedIdx, setFocusedIdx] = useState(0);
  const router = useRouter();

  // Fetch tracked products for live search
  const { data: productList } = useQuery({
    queryKey: ["cmd-products"],
    queryFn: () => api.listProducts({ limit: 100 }),
    staleTime: 1000 * 60 * 5,
    enabled: open,
  });

  const productItems: any[] = Array.isArray(productList)
    ? productList
    : (productList as any)?.items ?? [];

  // Filter static commands by query
  const filteredStatic = STATIC_COMMANDS.map((group) => ({
    ...group,
    items: group.items.filter(
      (item) => !query || item.label.toLowerCase().includes(query.toLowerCase())
    ),
  })).filter((g) => g.items.length > 0);

  // Live product results when query ≥ 2 chars
  const matchedProducts: CommandItem[] =
    query.length >= 2
      ? productItems
          .filter(
            (p: any) =>
              p.title?.toLowerCase().includes(query.toLowerCase()) ||
              p.asin?.toLowerCase().includes(query.toLowerCase())
          )
          .slice(0, 5)
          .map((p: any) => ({
            label: p.title ?? p.asin ?? "Unknown Product",
            icon: Tag,
            href: "/products",
            subtitle: [p.asin, p.marketplace, p.category].filter(Boolean).join(" · "),
          }))
      : [];

  const allGroups = [
    ...filteredStatic,
    ...(matchedProducts.length > 0
      ? [{ group: "Tracked Products", items: matchedProducts }]
      : []),
  ];

  const flatItems = allGroups.flatMap((g) => g.items);

  const handleSelect = useCallback(
    (item: CommandItem) => {
      const route = item.href;
      if (route) router.push(route);
      onClose();
      setQuery("");
      setFocusedIdx(0);
    },
    [router, onClose]
  );

  // Reset focus on query change
  useEffect(() => {
    setFocusedIdx(0);
  }, [query]);

  // Keyboard navigation
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        onClose();
        return;
      }
      if (!open) return;
      if (e.key === "ArrowDown") {
        e.preventDefault();
        setFocusedIdx((i) => Math.min(i + 1, flatItems.length - 1));
      }
      if (e.key === "ArrowUp") {
        e.preventDefault();
        setFocusedIdx((i) => Math.max(i - 1, 0));
      }
      if (e.key === "Enter") {
        e.preventDefault();
        if (flatItems[focusedIdx]) handleSelect(flatItems[focusedIdx]);
      }
    };
    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  }, [open, onClose, flatItems, focusedIdx, handleSelect]);

  // Track absolute item index across groups for focus highlight
  let itemCounter = 0;

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50"
          />
          <motion.div
            initial={{ opacity: 0, scale: 0.96, y: -20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.96, y: -20 }}
            transition={{ duration: 0.15 }}
            className="fixed top-[20%] left-1/2 -translate-x-1/2 w-[580px] bg-[#13141A] border border-white/10 rounded-2xl shadow-2xl overflow-hidden z-50"
          >
            {/* Search input */}
            <div className="flex items-center gap-3 px-4 py-3 border-b border-white/8">
              <Search className="w-4 h-4 text-white/30 flex-shrink-0" />
              <input
                autoFocus
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search pages, products, settings..."
                className="flex-1 bg-transparent text-sm text-white placeholder:text-white/25 outline-none"
              />
              {query && (
                <button
                  onClick={() => setQuery("")}
                  className="text-[10px] text-white/20 hover:text-white/50 bg-white/5 px-1.5 py-0.5 rounded transition-colors"
                >
                  Clear
                </button>
              )}
              <kbd className="text-[10px] text-white/20 bg-white/5 px-1.5 py-0.5 rounded flex-shrink-0">
                ESC
              </kbd>
            </div>

            {/* Results */}
            <div className="max-h-[420px] overflow-y-auto py-2">
              {flatItems.length === 0 ? (
                <div className="py-10 text-center">
                  <p className="text-xs text-white/25">No results for &ldquo;{query}&rdquo;</p>
                </div>
              ) : (
                allGroups.map((group) => (
                  <div key={group.group}>
                    <p className="px-4 py-2 text-[10px] font-semibold uppercase tracking-widest text-white/25">
                      {group.group}
                    </p>
                    {group.items.map((item) => {
                      const Icon = item.icon;
                      const idx = itemCounter++;
                      const isFocused = idx === focusedIdx;
                      return (
                        <button
                          key={`${item.label}-${idx}`}
                          onClick={() => handleSelect(item)}
                          className={cn(
                            "w-full flex items-center gap-3 px-4 py-2.5 transition-colors group",
                            isFocused ? "bg-violet-500/15" : "hover:bg-white/5"
                          )}
                        >
                          <div
                            className={cn(
                              "w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0",
                              isFocused ? "bg-violet-500/20" : "bg-white/5"
                            )}
                          >
                            <Icon
                              className={cn(
                                "w-3.5 h-3.5",
                                isFocused ? "text-violet-400" : "text-white/50"
                              )}
                            />
                          </div>

                          <div className="flex-1 text-left min-w-0">
                            <span
                              className={cn(
                                "text-sm block truncate transition-colors",
                                isFocused
                                  ? "text-violet-200"
                                  : "text-white/70 group-hover:text-white"
                              )}
                            >
                              {item.label}
                            </span>
                            {item.subtitle && (
                              <span className="text-[10px] text-white/30 truncate block">
                                {item.subtitle}
                              </span>
                            )}
                          </div>

                          {item.shortcut && (
                            <span className="text-[10px] text-white/20 flex-shrink-0">
                              {item.shortcut}
                            </span>
                          )}
                          <ArrowRight
                            className={cn(
                              "w-3 h-3 flex-shrink-0 transition-colors",
                              isFocused
                                ? "text-violet-400"
                                : "text-white/15 group-hover:text-white/40"
                            )}
                          />
                        </button>
                      );
                    })}
                  </div>
                ))
              )}
            </div>

            {/* Footer hints */}
            <div className="flex items-center gap-4 px-4 py-2 border-t border-white/5 text-[10px] text-white/20">
              <span className="flex items-center gap-1">
                <kbd className="bg-white/5 px-1 py-0.5 rounded">↑↓</kbd> navigate
              </span>
              <span className="flex items-center gap-1">
                <kbd className="bg-white/5 px-1 py-0.5 rounded">↵</kbd> select
              </span>
              <span className="flex items-center gap-1">
                <kbd className="bg-white/5 px-1 py-0.5 rounded">ESC</kbd> close
              </span>
              {productItems.length > 0 && (
                <span className="ml-auto text-white/15">
                  {productItems.length} products indexed
                </span>
              )}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
