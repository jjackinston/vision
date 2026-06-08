"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  Brain, CheckCircle2, ArrowRight, ShoppingCart, BarChart3,
  Target, DollarSign, Zap, Bot, Package, TrendingUp, Globe,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

/* ─── Types ─────────────────────────────────────────────────────────── */
interface OnboardingState {
  marketplaces: string[];
  revenueGoal: string;
  acosTarget: string;
  productCount: string;
  firstAsin: string;
}

/* ─── Constants ─────────────────────────────────────────────────────── */
const MARKETPLACES = [
  { id: "amazon",   label: "Amazon",      icon: "🛒", color: "border-amber-500/40  bg-amber-500/10  text-amber-400" },
  { id: "walmart",  label: "Walmart",     icon: "🏪", color: "border-blue-500/40   bg-blue-500/10   text-blue-400" },
  { id: "shopify",  label: "Shopify",     icon: "🛍️", color: "border-green-500/40  bg-green-500/10  text-green-400" },
  { id: "tiktok",   label: "TikTok Shop", icon: "📱", color: "border-pink-500/40   bg-pink-500/10   text-pink-400" },
  { id: "ebay",     label: "eBay",        icon: "🏷️", color: "border-red-500/40    bg-red-500/10    text-red-400" },
  { id: "etsy",     label: "Etsy",        icon: "🎨", color: "border-orange-500/40 bg-orange-500/10 text-orange-400" },
];

const REVENUE_OPTIONS = ["Under $10k/mo", "$10k–$50k/mo", "$50k–$200k/mo", "$200k–$1M/mo", "Over $1M/mo"];
const ACOS_OPTIONS    = ["Under 15%", "15–20%", "20–30%", "30%+", "Not sure yet"];
const PRODUCT_OPTIONS = ["1–5", "6–20", "21–100", "100+"];

const STEPS = [
  { id: 1, label: "Welcome"      },
  { id: 2, label: "Marketplaces" },
  { id: 3, label: "Goals"        },
  { id: 4, label: "First Product"},
  { id: 5, label: "Launch"       },
];

/* ─── Main Page ──────────────────────────────────────────────────────── */
export default function OnboardingPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [state, setState] = useState<OnboardingState>({
    marketplaces: ["amazon"],
    revenueGoal: "",
    acosTarget: "",
    productCount: "",
    firstAsin: "",
  });
  const [launching, setLaunching] = useState(false);

  const update = (patch: Partial<OnboardingState>) =>
    setState((s) => ({ ...s, ...patch }));

  const next = () => {
    if (step < 5) setStep((s) => s + 1);
  };

  const handleLaunch = async () => {
    setLaunching(true);
    // Save onboarding completion flag
    try { localStorage.setItem("sv_onboarded", "1"); } catch {}
    // Wait for the animation, then redirect
    await new Promise((r) => setTimeout(r, 3200));
    router.push("/dashboard");
  };

  return (
    <div className="min-h-screen bg-[#0A0B0E] flex flex-col items-center justify-center p-6">
      {/* Logo */}
      <div className="flex items-center gap-2 mb-8">
        <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-violet-500 to-blue-500 flex items-center justify-center">
          <Brain className="w-4 h-4 text-white" />
        </div>
        <span className="text-white font-bold text-lg">SellerVision AI</span>
      </div>

      {/* Progress bar */}
      <div className="flex items-center gap-2 mb-8">
        {STEPS.map((s, i) => (
          <div key={s.id} className="flex items-center gap-2">
            <div className={cn(
              "w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold transition-all duration-300",
              step > s.id
                ? "bg-violet-500 text-white"
                : step === s.id
                ? "bg-violet-500/30 text-violet-300 ring-2 ring-violet-500/50"
                : "bg-white/5 text-white/20"
            )}>
              {step > s.id ? <CheckCircle2 className="w-3.5 h-3.5" /> : s.id}
            </div>
            {i < STEPS.length - 1 && (
              <div className={cn(
                "w-10 h-px transition-all duration-500",
                step > s.id ? "bg-violet-500" : "bg-white/10"
              )} />
            )}
          </div>
        ))}
      </div>

      {/* Card */}
      <div className="w-full max-w-lg">
        <AnimatePresence mode="wait">
          <motion.div
            key={step}
            initial={{ opacity: 0, x: 30 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -30 }}
            transition={{ duration: 0.2 }}
            className="bg-[#13141A] border border-white/8 rounded-2xl p-8"
          >
            {step === 1 && <StepWelcome onNext={next} />}
            {step === 2 && <StepMarketplaces state={state} update={update} onNext={next} />}
            {step === 3 && <StepGoals state={state} update={update} onNext={next} />}
            {step === 4 && <StepFirstProduct state={state} update={update} onNext={next} />}
            {step === 5 && <StepLaunch state={state} launching={launching} onLaunch={handleLaunch} />}
          </motion.div>
        </AnimatePresence>
      </div>

      {/* Skip */}
      {step < 5 && (
        <button
          onClick={() => router.push("/dashboard")}
          className="mt-5 text-xs text-white/20 hover:text-white/40 transition-colors"
        >
          Skip setup → go to dashboard
        </button>
      )}
    </div>
  );
}

/* ─── Step 1: Welcome ────────────────────────────────────────────────── */
function StepWelcome({ onNext }: { onNext: () => void }) {
  return (
    <div className="text-center">
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ delay: 0.1 }}
        className="w-16 h-16 rounded-2xl bg-gradient-to-br from-violet-500 to-blue-500 flex items-center justify-center mx-auto mb-5"
      >
        <Brain className="w-8 h-8 text-white" />
      </motion.div>

      <h1 className="text-2xl font-black text-white mb-2">
        Welcome to SellerVision AI
      </h1>
      <p className="text-white/50 text-sm mb-6 leading-relaxed">
        Your autonomous AI platform for e-commerce growth. Let's take 60 seconds to
        personalize your experience.
      </p>

      <div className="grid grid-cols-2 gap-3 mb-8 text-left">
        {[
          { icon: Bot,        label: "7 AI Agents",       sub: "Working 24/7 autonomously" },
          { icon: TrendingUp, label: "Live Intelligence",  sub: "Real-time market data" },
          { icon: BarChart3,  label: "23 Modules",         sub: "Full platform coverage" },
          { icon: Zap,        label: "Instant Insights",   sub: "AI CEO daily briefings" },
        ].map(({ icon: Icon, label, sub }) => (
          <div key={label} className="bg-white/3 border border-white/5 rounded-xl p-3 flex items-start gap-2.5">
            <div className="w-7 h-7 rounded-lg bg-violet-500/15 flex items-center justify-center flex-shrink-0">
              <Icon className="w-3.5 h-3.5 text-violet-400" />
            </div>
            <div>
              <p className="text-xs font-semibold text-white">{label}</p>
              <p className="text-[10px] text-white/40">{sub}</p>
            </div>
          </div>
        ))}
      </div>

      <Button onClick={onNext} className="w-full bg-gradient-to-r from-violet-600 to-blue-600 hover:opacity-90 h-11">
        Let's get started
        <ArrowRight className="w-4 h-4 ml-2" />
      </Button>
    </div>
  );
}

/* ─── Step 2: Marketplaces ───────────────────────────────────────────── */
function StepMarketplaces({
  state, update, onNext,
}: { state: OnboardingState; update: (p: Partial<OnboardingState>) => void; onNext: () => void }) {
  const toggle = (id: string) => {
    const current = state.marketplaces;
    update({
      marketplaces: current.includes(id)
        ? current.filter((m) => m !== id)
        : [...current, id],
    });
  };

  return (
    <div>
      <ShoppingCart className="w-8 h-8 text-amber-400 mb-4" />
      <h2 className="text-xl font-bold text-white mb-1">Where do you sell?</h2>
      <p className="text-white/40 text-sm mb-6">Select all marketplaces you're active on.</p>

      <div className="grid grid-cols-2 gap-3 mb-8">
        {MARKETPLACES.map((mp) => {
          const active = state.marketplaces.includes(mp.id);
          return (
            <button
              key={mp.id}
              onClick={() => toggle(mp.id)}
              className={cn(
                "flex items-center gap-3 p-3.5 rounded-xl border transition-all text-left",
                active
                  ? mp.color
                  : "border-white/8 bg-white/3 text-white/40 hover:border-white/15"
              )}
            >
              <span className="text-xl">{mp.icon}</span>
              <span className="text-sm font-medium">{mp.label}</span>
              {active && <CheckCircle2 className="w-4 h-4 ml-auto" />}
            </button>
          );
        })}
      </div>

      <Button
        onClick={onNext}
        disabled={state.marketplaces.length === 0}
        className="w-full bg-violet-600 hover:bg-violet-500 h-11"
      >
        Continue <ArrowRight className="w-4 h-4 ml-2" />
      </Button>
    </div>
  );
}

/* ─── Step 3: Goals ──────────────────────────────────────────────────── */
function StepGoals({
  state, update, onNext,
}: { state: OnboardingState; update: (p: Partial<OnboardingState>) => void; onNext: () => void }) {
  return (
    <div>
      <Target className="w-8 h-8 text-emerald-400 mb-4" />
      <h2 className="text-xl font-bold text-white mb-1">Set your targets</h2>
      <p className="text-white/40 text-sm mb-6">Your AI agents will optimize toward these goals.</p>

      <div className="space-y-5 mb-8">
        {/* Revenue goal */}
        <div>
          <label className="text-xs font-semibold uppercase text-white/30 block mb-2">
            <DollarSign className="w-3 h-3 inline mr-1" />Monthly Revenue Goal
          </label>
          <div className="grid grid-cols-2 gap-2">
            {REVENUE_OPTIONS.map((o) => (
              <button
                key={o}
                onClick={() => update({ revenueGoal: o })}
                className={cn(
                  "text-xs py-2 px-3 rounded-lg border transition-all text-left",
                  state.revenueGoal === o
                    ? "border-emerald-500/50 bg-emerald-500/10 text-emerald-400"
                    : "border-white/8 bg-white/3 text-white/40 hover:border-white/15"
                )}
              >{o}</button>
            ))}
          </div>
        </div>

        {/* ACoS target */}
        <div>
          <label className="text-xs font-semibold uppercase text-white/30 block mb-2">
            <BarChart3 className="w-3 h-3 inline mr-1" />Target ACoS
          </label>
          <div className="grid grid-cols-3 gap-2">
            {ACOS_OPTIONS.map((o) => (
              <button
                key={o}
                onClick={() => update({ acosTarget: o })}
                className={cn(
                  "text-xs py-2 px-3 rounded-lg border transition-all",
                  state.acosTarget === o
                    ? "border-violet-500/50 bg-violet-500/10 text-violet-400"
                    : "border-white/8 bg-white/3 text-white/40 hover:border-white/15"
                )}
              >{o}</button>
            ))}
          </div>
        </div>

        {/* Product count */}
        <div>
          <label className="text-xs font-semibold uppercase text-white/30 block mb-2">
            <Package className="w-3 h-3 inline mr-1" />Number of Active Products
          </label>
          <div className="grid grid-cols-4 gap-2">
            {PRODUCT_OPTIONS.map((o) => (
              <button
                key={o}
                onClick={() => update({ productCount: o })}
                className={cn(
                  "text-xs py-2 px-3 rounded-lg border transition-all",
                  state.productCount === o
                    ? "border-blue-500/50 bg-blue-500/10 text-blue-400"
                    : "border-white/8 bg-white/3 text-white/40 hover:border-white/15"
                )}
              >{o}</button>
            ))}
          </div>
        </div>
      </div>

      <Button
        onClick={onNext}
        disabled={!state.revenueGoal || !state.acosTarget || !state.productCount}
        className="w-full bg-violet-600 hover:bg-violet-500 h-11"
      >
        Continue <ArrowRight className="w-4 h-4 ml-2" />
      </Button>
    </div>
  );
}

/* ─── Step 4: First Product ──────────────────────────────────────────── */
function StepFirstProduct({
  state, update, onNext,
}: { state: OnboardingState; update: (p: Partial<OnboardingState>) => void; onNext: () => void }) {
  return (
    <div>
      <Package className="w-8 h-8 text-blue-400 mb-4" />
      <h2 className="text-xl font-bold text-white mb-1">Add your first product</h2>
      <p className="text-white/40 text-sm mb-6">
        Enter an ASIN to start tracking — or skip and add products later from the dashboard.
      </p>

      <div className="mb-6">
        <label className="text-[10px] font-semibold uppercase text-white/30 block mb-2">Amazon ASIN</label>
        <input
          value={state.firstAsin}
          onChange={(e) => update({ firstAsin: e.target.value.toUpperCase().trim() })}
          placeholder="e.g. B08XYZ1234"
          maxLength={10}
          className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm text-white font-mono placeholder:text-white/20 outline-none focus:border-blue-500/50"
        />
        <p className="text-[10px] text-white/25 mt-2">
          We'll pull live data, reviews, BSR, and competitor intel automatically.
        </p>
      </div>

      <div className="space-y-2">
        <Button onClick={onNext} className="w-full bg-violet-600 hover:bg-violet-500 h-11">
          {state.firstAsin ? "Track this product & continue" : "Skip for now"}
          <ArrowRight className="w-4 h-4 ml-2" />
        </Button>
      </div>
    </div>
  );
}

/* ─── Step 5: Launch ─────────────────────────────────────────────────── */
const AGENT_LIST = [
  { label: "Product Research Agent",     color: "text-violet-400", delay: 0    },
  { label: "Trend Detection Agent",      color: "text-blue-400",   delay: 0.3  },
  { label: "Competitor Analysis Agent",  color: "text-amber-400",  delay: 0.6  },
  { label: "Inventory Planning Agent",   color: "text-red-400",    delay: 0.9  },
  { label: "PPC Optimization Agent",     color: "text-emerald-400",delay: 1.2  },
  { label: "Supplier Intelligence Agent",color: "text-pink-400",   delay: 1.5  },
  { label: "Listing Optimization Agent", color: "text-sky-400",    delay: 1.8  },
];

function StepLaunch({
  state, launching, onLaunch,
}: { state: OnboardingState; launching: boolean; onLaunch: () => void }) {
  return (
    <div className="text-center">
      <motion.div
        animate={launching ? { rotate: 360 } : {}}
        transition={{ repeat: Infinity, duration: 1.5, ease: "linear" }}
        className="w-14 h-14 rounded-2xl bg-gradient-to-br from-violet-500 to-blue-500 flex items-center justify-center mx-auto mb-5"
      >
        {launching
          ? <Zap className="w-7 h-7 text-white" />
          : <Bot className="w-7 h-7 text-white" />
        }
      </motion.div>

      <h2 className="text-xl font-bold text-white mb-1">
        {launching ? "Launching your AI fleet…" : "You're all set!"}
      </h2>
      <p className="text-white/40 text-sm mb-6">
        {launching
          ? "Booting agents and loading your personalized dashboard."
          : `Your ${state.marketplaces.length} marketplace${state.marketplaces.length > 1 ? "s" : ""} are configured. Your AI agents will start working immediately.`
        }
      </p>

      {/* Agent boot list */}
      <div className="bg-white/3 border border-white/5 rounded-xl p-4 mb-6 text-left space-y-2">
        {AGENT_LIST.map(({ label, color, delay }) => (
          <motion.div
            key={label}
            initial={{ opacity: 0, x: -10 }}
            animate={launching ? { opacity: 1, x: 0 } : { opacity: 0.4 }}
            transition={{ delay, duration: 0.3 }}
            className="flex items-center gap-2.5"
          >
            <motion.div
              animate={launching ? { scale: [1, 1.3, 1] } : {}}
              transition={{ delay, duration: 0.4 }}
              className={cn("w-1.5 h-1.5 rounded-full flex-shrink-0",
                launching ? "bg-emerald-500" : "bg-white/20")}
            />
            <span className={cn("text-xs", launching ? color : "text-white/30")}>{label}</span>
            {launching && (
              <motion.span
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: delay + 0.3 }}
                className="ml-auto text-[9px] text-emerald-400"
              >
                Online ✓
              </motion.span>
            )}
          </motion.div>
        ))}
      </div>

      {/* Marketplace recap */}
      {!launching && (
        <div className="flex items-center justify-center gap-2 mb-6 flex-wrap">
          {state.marketplaces.map((id) => {
            const mp = MARKETPLACES.find((m) => m.id === id);
            return mp ? (
              <span key={id} className="text-xs bg-white/5 border border-white/8 px-2.5 py-1 rounded-full text-white/60">
                {mp.icon} {mp.label}
              </span>
            ) : null;
          })}
        </div>
      )}

      {!launching && (
        <Button
          onClick={onLaunch}
          className="w-full bg-gradient-to-r from-violet-600 to-blue-600 hover:opacity-90 h-11 text-sm font-semibold"
        >
          <Zap className="w-4 h-4 mr-2" />
          Launch my AI platform
        </Button>
      )}

      {launching && (
        <div className="flex items-center justify-center gap-2 text-xs text-white/30">
          <Globe className="w-3.5 h-3.5 animate-spin" />
          Redirecting to your dashboard…
        </div>
      )}
    </div>
  );
}
