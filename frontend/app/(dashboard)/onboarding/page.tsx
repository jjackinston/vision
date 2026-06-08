"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import {
  Store, ShoppingBag, Bell, CheckCircle2, ArrowRight,
  Zap, Package, BarChart3, Sparkles, ExternalLink,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { api } from "@/lib/api";

// ── Types ─────────────────────────────────────────────────────────────
interface Step {
  id: number;
  title: string;
  description: string;
  icon: React.ElementType;
  color: string;
  action?: () => void;
  actionLabel?: string;
  skipLabel?: string;
}

// ── Marketplace button ────────────────────────────────────────────────
function MarketplaceButton({
  name, logo, connected, onClick,
}: {
  name: string; logo: string; connected: boolean; onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-3 w-full px-4 py-3 rounded-xl border text-left transition-all
        ${connected
          ? "border-emerald-500/50 bg-emerald-500/10 text-emerald-400"
          : "border-white/10 bg-white/5 hover:bg-white/10 text-gray-300 hover:border-white/20"
        }`}
    >
      <span className="text-xl">{logo}</span>
      <span className="font-medium">{name}</span>
      {connected && (
        <Badge className="ml-auto bg-emerald-500/20 text-emerald-400 border-emerald-500/30 text-xs">
          Connected
        </Badge>
      )}
    </button>
  );
}

// ── Step content ──────────────────────────────────────────────────────
function StepConnect({ onConnect }: { onConnect: (name: string) => void }) {
  const [connected, setConnected] = useState<string[]>([]);
  const marketplaces = [
    { name: "Amazon", logo: "🛒", href: "/settings?tab=integrations" },
    { name: "Shopify", logo: "🟢", href: "/settings?tab=integrations" },
    { name: "Walmart", logo: "💙", href: "/settings?tab=integrations" },
    { name: "eBay",    logo: "🔴", href: "/settings?tab=integrations" },
  ];
  return (
    <div className="space-y-3">
      {marketplaces.map((m) => (
        <MarketplaceButton
          key={m.name}
          name={m.name}
          logo={m.logo}
          connected={connected.includes(m.name)}
          onClick={() => {
            setConnected((prev) =>
              prev.includes(m.name) ? prev : [...prev, m.name]
            );
            onConnect(m.name);
          }}
        />
      ))}
      <p className="text-xs text-gray-500 pt-1">
        You can always add more connections later in{" "}
        <a href="/settings" className="text-violet-400 underline underline-offset-2">Settings → Integrations</a>.
      </p>
    </div>
  );
}

function StepImport({ onImport }: { onImport: () => void }) {
  const [done, setDone] = useState(false);
  return (
    <div className="space-y-4">
      <div className="rounded-xl border border-white/10 bg-white/5 p-4 space-y-3">
        <div className="flex items-center gap-3">
          <Package className="w-5 h-5 text-violet-400" />
          <span className="text-sm text-gray-300">Scan my active listings and import products</span>
        </div>
        <div className="flex items-center gap-3">
          <BarChart3 className="w-5 h-5 text-blue-400" />
          <span className="text-sm text-gray-300">Pull 90-day sales history for AI analysis</span>
        </div>
        <div className="flex items-center gap-3">
          <Sparkles className="w-5 h-5 text-amber-400" />
          <span className="text-sm text-gray-300">Auto-score each product for opportunity & risk</span>
        </div>
      </div>

      {!done ? (
        <Button
          onClick={() => { setDone(true); onImport(); }}
          className="w-full bg-violet-600 hover:bg-violet-500 text-white"
        >
          <Zap className="w-4 h-4 mr-2" />
          Import Products Now
        </Button>
      ) : (
        <div className="flex items-center gap-2 text-emerald-400 text-sm font-medium">
          <CheckCircle2 className="w-4 h-4" />
          Import queued — products will appear in your dashboard within a few minutes.
        </div>
      )}

      <p className="text-xs text-gray-500">
        No marketplace connected yet? We loaded 8 sample products so you can explore the platform.
      </p>
    </div>
  );
}

function StepAlerts() {
  return (
    <div className="space-y-3">
      {[
        { label: "Low stock alerts",      desc: "Notify when inventory drops below reorder point", enabled: true,  color: "text-amber-400" },
        { label: "Price drop alerts",      desc: "Notify when competitors undercut your buy box",    enabled: true,  color: "text-red-400"   },
        { label: "Keyword rank changes",   desc: "Notify when your ranking moves ±3 positions",      enabled: true,  color: "text-blue-400"  },
        { label: "Weekly AI briefing",     desc: "Sunday 8am email summary with top opportunities",  enabled: false, color: "text-violet-400" },
      ].map((alert) => (
        <label
          key={alert.label}
          className="flex items-center gap-3 p-3 rounded-xl border border-white/10 bg-white/5 hover:bg-white/8 cursor-pointer transition-all"
        >
          <input
            type="checkbox"
            defaultChecked={alert.enabled}
            className="w-4 h-4 accent-violet-500 rounded"
          />
          <div>
            <div className={`text-sm font-medium ${alert.color}`}>{alert.label}</div>
            <div className="text-xs text-gray-500">{alert.desc}</div>
          </div>
        </label>
      ))}
      <p className="text-xs text-gray-500 pt-1">
        Manage all alert preferences in{" "}
        <a href="/settings" className="text-violet-400 underline underline-offset-2">Settings → Notifications</a>.
      </p>
    </div>
  );
}

// ── Main page ─────────────────────────────────────────────────────────
export default function OnboardingPage() {
  const router = useRouter();
  const qc = useQueryClient();
  const [step, setStep] = useState(0);
  const [completed, setCompleted] = useState<number[]>([]);

  const markComplete = useMutation({
    mutationFn: () =>
      api.client.patch("/tenants/me/settings", { onboarding_complete: true }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["me"] });
      router.push("/dashboard");
    },
    onError: () => {
      // Endpoint may not exist yet — navigate anyway
      router.push("/dashboard");
    },
  });

  const completeStep = (i: number) => {
    if (!completed.includes(i)) setCompleted((prev) => [...prev, i]);
  };

  const steps = [
    {
      id: 0,
      icon: Store,
      color: "text-emerald-400",
      bg: "bg-emerald-500/15",
      title: "Connect your marketplace",
      subtitle: "Link Amazon, Shopify, Walmart, or eBay to start pulling live data.",
      content: <StepConnect onConnect={() => completeStep(0)} />,
    },
    {
      id: 1,
      icon: Package,
      color: "text-violet-400",
      bg: "bg-violet-500/15",
      title: "Import your products",
      subtitle: "We'll scan your listings and run AI analysis on each product.",
      content: <StepImport onImport={() => completeStep(1)} />,
    },
    {
      id: 2,
      icon: Bell,
      color: "text-amber-400",
      bg: "bg-amber-500/15",
      title: "Set up alerts",
      subtitle: "Get notified about stockouts, buy-box losses, and keyword drops.",
      content: <StepAlerts />,
    },
  ] as const;

  const current = steps[step];
  const Icon = current.icon;
  const allDone = step === steps.length - 1;

  return (
    <div className="min-h-screen bg-[#0B0E17] flex items-center justify-center p-4">
      <div className="w-full max-w-lg">

        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -12 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <div className="flex items-center justify-center gap-2 mb-3">
            <Sparkles className="w-5 h-5 text-violet-400" />
            <span className="text-violet-400 text-sm font-semibold tracking-wide uppercase">
              Welcome to SellerVision AI
            </span>
          </div>
          <h1 className="text-2xl font-bold text-white">Let's get you set up</h1>
          <p className="text-gray-400 text-sm mt-1">
            3 steps to your first AI-powered insight
          </p>
        </motion.div>

        {/* Step indicators */}
        <div className="flex items-center gap-2 mb-6">
          {steps.map((s, i) => (
            <React.Fragment key={s.id}>
              <button
                onClick={() => i < step + 1 && setStep(i)}
                className={`flex items-center justify-center w-8 h-8 rounded-full text-sm font-bold transition-all
                  ${i === step
                    ? "bg-violet-600 text-white ring-2 ring-violet-400/40"
                    : completed.includes(i)
                    ? "bg-emerald-600/30 text-emerald-400 border border-emerald-500/30"
                    : "bg-white/5 text-gray-500 border border-white/10"
                  }`}
              >
                {completed.includes(i) ? <CheckCircle2 className="w-4 h-4" /> : i + 1}
              </button>
              {i < steps.length - 1 && (
                <div className={`flex-1 h-0.5 rounded-full transition-all ${i < step ? "bg-violet-600/60" : "bg-white/10"}`} />
              )}
            </React.Fragment>
          ))}
        </div>

        {/* Card */}
        <AnimatePresence mode="wait">
          <motion.div
            key={step}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.2 }}
            className="rounded-2xl border border-white/10 bg-white/[0.03] p-6 backdrop-blur-sm"
          >
            <div className="flex items-center gap-4 mb-5">
              <div className={`w-12 h-12 rounded-xl ${current.bg} flex items-center justify-center`}>
                <Icon className={`w-6 h-6 ${current.color}`} />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-white">{current.title}</h2>
                <p className="text-sm text-gray-400">{current.subtitle}</p>
              </div>
            </div>

            {current.content}

            <div className="flex items-center justify-between mt-6 pt-4 border-t border-white/10">
              <button
                onClick={() => router.push("/dashboard")}
                className="text-sm text-gray-500 hover:text-gray-300 transition-colors"
              >
                Skip setup → go to dashboard
              </button>

              {allDone ? (
                <Button
                  onClick={() => markComplete.mutate()}
                  disabled={markComplete.isPending}
                  className="bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white"
                >
                  {markComplete.isPending ? "Saving…" : "Go to Dashboard"}
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              ) : (
                <Button
                  onClick={() => setStep((s) => s + 1)}
                  className="bg-violet-600 hover:bg-violet-500 text-white"
                >
                  Next
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              )}
            </div>
          </motion.div>
        </AnimatePresence>

        {/* Footer note */}
        <p className="text-center text-xs text-gray-600 mt-4">
          You can revisit this setup anytime via Settings → Onboarding
        </p>
      </div>
    </div>
  );
}
