"use client";

/**
 * Mobile navigation components:
 *
 * <MobileDrawer open onClose>  — Slide-in left drawer with full nav tree.
 *                                 Opens when hamburger is tapped.
 * <MobileBottomNav>            — Fixed 5-tab bottom tab bar (md:hidden).
 */

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Brain, Search, BarChart3, Package, Bot, Settings,
  Target, TrendingUp, Lightbulb, FileText, DollarSign,
  Warehouse, Zap, ShoppingBag, Cpu, X,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Sheet } from "@/components/ui/sheet";
import { Badge } from "@/components/ui/badge";

// ── Nav tree (mirrors dashboard layout) ────────────────────────────────

const SECTIONS = [
  {
    section: "Intelligence",
    items: [
      { name: "AI CEO Dashboard",    href: "/dashboard",  icon: Brain,      badge: "AI",   badgeColor: "purple" },
      { name: "Product Research",    href: "/products",   icon: Search },
      { name: "Keyword Intelligence",href: "/keywords",   icon: Target },
      { name: "Competitor Analysis", href: "/competitors",icon: TrendingUp },
      { name: "Trend Discovery",     href: "/trends",     icon: Lightbulb,  badge: "Live" },
    ],
  },
  {
    section: "Operations",
    items: [
      { name: "Inventory Hub",    href: "/inventory", icon: Package },
      { name: "Listing Manager",  href: "/listings",  icon: FileText },
      { name: "PPC Manager",      href: "/ppc",       icon: DollarSign },
      { name: "Suppliers",        href: "/suppliers", icon: Warehouse },
    ],
  },
  {
    section: "Analytics",
    items: [
      { name: "Analytics", href: "/analytics", icon: BarChart3 },
    ],
  },
  {
    section: "AI Platform",
    items: [
      { name: "AI Agents",   href: "/agents",      icon: Bot,          badge: "New" },
      { name: "Automation",  href: "/automation",  icon: Zap },
      { name: "Marketplace", href: "/marketplace", icon: ShoppingBag },
    ],
  },
  {
    section: "Account",
    items: [
      { name: "Settings",     href: "/settings",              icon: Settings },
      { name: "Integrations", href: "/settings/integrations", icon: Cpu },
    ],
  },
];

// ── Bottom tab bar items (5 most-visited) ──────────────────────────────

const BOTTOM_TABS = [
  { name: "Dashboard", href: "/dashboard", icon: Brain },
  { name: "Products",  href: "/products",  icon: Search },
  { name: "Analytics", href: "/analytics", icon: BarChart3 },
  { name: "Agents",    href: "/agents",    icon: Bot },
  { name: "Settings",  href: "/settings",  icon: Settings },
];

// ── MobileDrawer ───────────────────────────────────────────────────────

export function MobileDrawer({ open, onClose }: { open: boolean; onClose: () => void }) {
  const pathname = usePathname();

  return (
    <Sheet open={open} onClose={onClose} side="left" showClose={false}>
      <div className="flex flex-col h-full">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-white/8">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-500 to-blue-500 flex items-center justify-center">
              <Brain className="w-4 h-4 text-white" />
            </div>
            <div>
              <p className="text-sm font-bold text-white leading-none">SellerVision</p>
              <p className="text-[10px] text-violet-400 font-medium">AI Platform</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-lg text-gray-500 hover:text-white hover:bg-white/10 transition-all"
            aria-label="Close menu"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Nav */}
        <nav className="flex-1 overflow-y-auto py-4 px-3 space-y-5">
          {SECTIONS.map((section) => (
            <div key={section.section}>
              <p className="px-2 mb-2 text-[10px] font-semibold uppercase tracking-widest text-white/30">
                {section.section}
              </p>
              <ul className="space-y-0.5">
                {section.items.map((item) => {
                  const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
                  const Icon = item.icon;
                  return (
                    <li key={item.name}>
                      <Link
                        href={item.href}
                        onClick={onClose}
                        className={cn(
                          "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all min-h-[44px]",
                          isActive
                            ? "bg-violet-500/15 text-violet-300"
                            : "text-white/60 hover:text-white hover:bg-white/5 active:bg-white/10"
                        )}
                      >
                        <Icon className={cn("w-4 h-4 flex-shrink-0", isActive && "text-violet-400")} />
                        <span className="flex-1">{item.name}</span>
                        {item.badge && (
                          <Badge
                            variant="outline"
                            className={cn(
                              "text-[9px] px-1.5 py-0 h-4 border-0",
                              (item as any).badgeColor === "purple"
                                ? "bg-violet-500/20 text-violet-300"
                                : "bg-emerald-500/20 text-emerald-400"
                            )}
                          >
                            {item.badge}
                          </Badge>
                        )}
                      </Link>
                    </li>
                  );
                })}
              </ul>
            </div>
          ))}
        </nav>

        {/* Footer */}
        <div className="px-5 py-4 border-t border-white/8">
          <p className="text-[11px] text-gray-600 text-center">SellerVision AI v1.0</p>
        </div>
      </div>
    </Sheet>
  );
}

// ── MobileBottomNav ───────────────────────────────────────────────────

export function MobileBottomNav() {
  const pathname = usePathname();

  return (
    <nav
      className="flex md:hidden fixed bottom-0 left-0 right-0 z-30
        bg-[#0D0E12]/95 backdrop-blur-md border-t border-white/8
        safe-area-inset-bottom"
      aria-label="Mobile navigation"
    >
      <div className="flex w-full">
        {BOTTOM_TABS.map((tab) => {
          const isActive = pathname === tab.href || pathname.startsWith(tab.href + "/");
          const Icon = tab.icon;
          return (
            <Link
              key={tab.href}
              href={tab.href}
              className={cn(
                "flex-1 flex flex-col items-center justify-center gap-1 py-3 min-h-[56px]",
                "text-[10px] font-medium transition-colors active:bg-white/5",
                isActive ? "text-violet-400" : "text-gray-500 hover:text-gray-300"
              )}
              aria-current={isActive ? "page" : undefined}
            >
              <Icon className={cn("w-5 h-5 transition-transform", isActive && "scale-110")} />
              <span>{tab.name}</span>
              {isActive && (
                <span className="absolute top-0 h-0.5 w-8 bg-violet-400 rounded-full" />
              )}
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
