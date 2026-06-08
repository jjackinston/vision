"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import {
  Brain, TrendingUp, Package, Target, Zap, BarChart3, Bot,
  Shield, Globe, ArrowRight, Star, CheckCircle2, Sparkles,
  DollarSign, Search, Lightbulb, Users, ChevronRight,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

const FEATURES = [
  { icon: Brain, title: "AI CEO Dashboard", desc: "Daily action plans, not just charts. Your AI executive makes the decisions.", color: "violet" },
  { icon: Search, title: "Product Opportunity Engine", desc: "Scores every product on 5 AI dimensions. Find winners before competitors.", color: "blue" },
  { icon: TrendingUp, title: "Trend Prediction", desc: "Detects viral trends on TikTok, Reddit, Pinterest 30-90 days before Amazon peaks.", color: "emerald" },
  { icon: Target, title: "PPC Intelligence", desc: "Autonomous bid optimization. Targets ACoS < 20% with AI-driven adjustments.", color: "amber" },
  { icon: Package, title: "Inventory Command Center", desc: "Never stockout. AI predicts demand and auto-generates purchase orders.", color: "orange" },
  { icon: Bot, title: "7 Autonomous AI Agents", desc: "Product, Trend, Competitor, PPC, Inventory, Supplier, Listing agents working 24/7.", color: "pink" },
  { icon: BarChart3, title: "Digital Twin", desc: "Simulate your business before spending. What-if scenarios with financial projections.", color: "teal" },
  { icon: Globe, title: "Multi-Platform Intelligence", desc: "Amazon, Walmart, Shopify, TikTok, eBay, Etsy — unified view, one platform.", color: "blue" },
];

const PLATFORMS = ["Amazon", "Walmart", "Shopify", "TikTok Shop", "eBay", "Etsy", "AliExpress", "Google Shopping"];

const TESTIMONIALS = [
  { name: "Sarah Chen", role: "7-Figure Amazon Seller", text: "SellerVision found me a product opportunity my competitors missed. $180K in year-one revenue.", avatar: "SC" },
  { name: "Marcus Williams", role: "E-Commerce Aggregator", text: "We manage 14 brands. The AI CEO dashboard replaced 3 full-time analysts.", avatar: "MW" },
  { name: "Priya Sharma", role: "Shopify Brand Owner", text: "The PPC agent reduced our ACoS from 34% to 18% in 45 days. Unbelievable.", avatar: "PS" },
];

const PLANS = [
  { name: "Starter", price: 49, description: "Individual sellers just getting started", features: ["3 Marketplaces", "500 product lookups/mo", "AI CEO Dashboard", "Basic keyword research", "Email support"], cta: "Start Free Trial", highlight: false },
  { name: "Professional", price: 149, description: "Serious sellers scaling their business", features: ["All Marketplaces", "Unlimited lookups", "All 7 AI Agents", "PPC Intelligence", "Digital Twin", "Priority support"], cta: "Start Free Trial", highlight: true },
  { name: "Business", price: 349, description: "Multi-brand operators and agencies", features: ["Everything in Pro", "5 team members", "White-label reports", "API access", "Custom agents", "Dedicated CSM"], cta: "Contact Sales", highlight: false },
];

const STATS = [
  { value: "50K+", label: "Active Sellers" },
  { value: "$2.1B+", label: "Revenue Tracked" },
  { value: "7", label: "AI Agents" },
  { value: "6", label: "Marketplaces" },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[#0A0B0E] text-white overflow-x-hidden">
      {/* Nav */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-[#0A0B0E]/90 backdrop-blur-xl border-b border-white/5">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-500 to-blue-500 flex items-center justify-center">
              <Brain className="w-4 h-4 text-white" />
            </div>
            <span className="font-bold text-white">SellerVision AI</span>
            <Badge className="bg-violet-500/20 text-violet-300 border-0 text-[10px]">BETA</Badge>
          </div>
          <div className="hidden md:flex items-center gap-8 text-sm text-white/60">
            <a href="#features" className="hover:text-white transition-colors">Features</a>
            <a href="#pricing" className="hover:text-white transition-colors">Pricing</a>
            <a href="#testimonials" className="hover:text-white transition-colors">Reviews</a>
          </div>
          <div className="flex items-center gap-3">
            <Link href="/login">
              <Button variant="ghost" size="sm" className="text-white/60 hover:text-white text-xs">Log in</Button>
            </Link>
            <Link href="/register">
              <Button size="sm" className="bg-violet-600 hover:bg-violet-500 text-xs">
                Start Free Trial
                <ArrowRight className="w-3.5 h-3.5 ml-1.5" />
              </Button>
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="pt-40 pb-24 px-6 text-center relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-violet-500/5 via-transparent to-transparent" />
        <div className="absolute top-20 left-1/2 -translate-x-1/2 w-[600px] h-[300px] bg-violet-500/8 rounded-full blur-[80px]" />

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="relative max-w-4xl mx-auto"
        >
          <Badge className="bg-violet-500/20 text-violet-300 border border-violet-500/30 text-xs px-3 py-1 mb-6 inline-flex items-center gap-1.5">
            <Sparkles className="w-3 h-3" />
            The Bloomberg Terminal + Salesforce + ChatGPT for E-Commerce
          </Badge>

          <h1 className="text-5xl md:text-7xl font-black mb-6 leading-[1.05] tracking-tight">
            Your AI E-Commerce{" "}
            <span className="bg-gradient-to-r from-violet-400 via-pink-400 to-blue-400 bg-clip-text text-transparent">
              Command Center
            </span>
          </h1>

          <p className="text-lg md:text-xl text-white/50 max-w-2xl mx-auto mb-8 leading-relaxed">
            SellerVision AI doesn't just show you data. It tells you what will happen next, why it will happen,
            and exactly what to do about it — across Amazon, Walmart, Shopify, TikTok Shop, and more.
          </p>

          <div className="flex items-center justify-center gap-4 mb-8">
            <Link href="/register">
              <Button size="lg" className="bg-gradient-to-r from-violet-600 to-blue-600 hover:opacity-90 text-sm px-8 h-12">
                Start Free 14-Day Trial
                <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            </Link>
            <Link href="/dashboard">
              <Button variant="outline" size="lg" className="border-white/10 bg-white/5 text-white hover:bg-white/10 text-sm px-6 h-12">
                View Live Demo
              </Button>
            </Link>
          </div>

          <p className="text-xs text-white/30">No credit card required · Cancel anytime · 14-day free trial</p>
        </motion.div>

        {/* Stats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.6 }}
          className="flex items-center justify-center gap-12 mt-16"
        >
          {STATS.map((stat) => (
            <div key={stat.label} className="text-center">
              <p className="text-3xl font-black text-white mb-1">{stat.value}</p>
              <p className="text-xs text-white/40">{stat.label}</p>
            </div>
          ))}
        </motion.div>
      </section>

      {/* Platform logos */}
      <section className="py-10 border-y border-white/5 bg-white/[0.015]">
        <div className="max-w-5xl mx-auto px-6">
          <p className="text-center text-xs text-white/25 uppercase tracking-widest mb-6">Connected to all major marketplaces</p>
          <div className="flex items-center justify-center gap-8 flex-wrap">
            {PLATFORMS.map((p) => (
              <span key={p} className="text-sm font-semibold text-white/25 hover:text-white/60 transition-colors">{p}</span>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-24 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <Badge className="bg-violet-500/20 text-violet-300 border-0 text-xs mb-4">23 AI-Powered Modules</Badge>
            <h2 className="text-4xl font-black mb-4">
              Not a tool. An AI{" "}
              <span className="text-violet-400">business partner.</span>
            </h2>
            <p className="text-white/50 max-w-xl mx-auto">
              Every module is built to replace or augment an entire function of your e-commerce business — with AI that never sleeps.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {FEATURES.map((feature, i) => {
              const Icon = feature.icon;
              return (
                <motion.div
                  key={feature.title}
                  initial={{ opacity: 0, y: 16 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.05 }}
                  className="bg-[#111218] border border-white/5 rounded-xl p-5 hover:border-white/10 transition-all group"
                >
                  <div className={`w-8 h-8 rounded-lg bg-${feature.color}-500/20 flex items-center justify-center mb-3`}>
                    <Icon className={`w-4 h-4 text-${feature.color}-400`} />
                  </div>
                  <h3 className="text-sm font-bold text-white mb-2 group-hover:text-violet-300 transition-colors">{feature.title}</h3>
                  <p className="text-xs text-white/45 leading-relaxed">{feature.desc}</p>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* AI CEO section */}
      <section className="py-24 px-6 bg-gradient-to-b from-violet-500/5 to-transparent">
        <div className="max-w-6xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
            <div>
              <Badge className="bg-violet-500/20 text-violet-300 border-0 text-xs mb-4">Module 18 — AI CEO Dashboard</Badge>
              <h2 className="text-4xl font-black mb-6">
                Instead of charts,<br />
                <span className="text-violet-400">get decisions.</span>
              </h2>
              <p className="text-white/50 mb-8 leading-relaxed">
                Most tools show you what happened. SellerVision AI tells you what to do next —
                with specific instructions, expected ROI, and urgency levels.
              </p>
              <div className="space-y-4">
                {[
                  { action: "Reorder 500 units of Product B", impact: "+$8,400 avoided lost revenue", urgency: "critical" },
                  { action: "Increase Widget Pro price by 7%", impact: "+$1,200/mo profit", urgency: "high" },
                  { action: "Pause 3 high-ACoS keywords", impact: "-$340/mo wasted spend", urgency: "high" },
                  { action: "Expand to Walmart Marketplace", impact: "+$3,200/mo revenue", urgency: "medium" },
                ].map((item, i) => (
                  <div key={i} className="flex items-start gap-3 p-3 bg-[#111218] rounded-lg border border-white/5">
                    <div className={`w-2 h-2 rounded-full mt-1.5 flex-shrink-0 ${
                      item.urgency === "critical" ? "bg-red-400" :
                      item.urgency === "high" ? "bg-amber-400" : "bg-blue-400"
                    }`} />
                    <div className="flex-1">
                      <p className="text-sm text-white font-medium">{item.action}</p>
                      <p className="text-xs text-emerald-400">{item.impact}</p>
                    </div>
                    <ChevronRight className="w-4 h-4 text-white/20 flex-shrink-0" />
                  </div>
                ))}
              </div>
            </div>
            <div className="bg-[#111218] rounded-2xl border border-white/5 p-6">
              <div className="flex items-center gap-2 mb-4">
                <Brain className="w-4 h-4 text-violet-400" />
                <span className="text-sm font-semibold text-white">Business Health Score</span>
                <span className="ml-auto text-2xl font-black text-emerald-400">72/100</span>
              </div>
              <div className="space-y-3">
                {[
                  { label: "Revenue Growth", value: "+14.6%", good: true },
                  { label: "Avg ACoS", value: "18.4%", good: true },
                  { label: "Stockout Risk", value: "2 products", good: false },
                  { label: "Opportunities Found", value: "5 this week", good: true },
                ].map((m) => (
                  <div key={m.label} className="flex items-center justify-between p-2 bg-white/3 rounded-lg">
                    <span className="text-xs text-white/50">{m.label}</span>
                    <span className={`text-xs font-semibold ${m.good ? "text-emerald-400" : "text-amber-400"}`}>{m.value}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section id="testimonials" className="py-24 px-6">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-black mb-4">Sellers who switched, never looked back</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {TESTIMONIALS.map((t, i) => (
              <motion.div
                key={t.name}
                initial={{ opacity: 0, y: 12 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="bg-[#111218] border border-white/5 rounded-xl p-6"
              >
                <div className="flex mb-3">
                  {Array.from({ length: 5 }).map((_, j) => (
                    <Star key={j} className="w-3.5 h-3.5 text-amber-400 fill-amber-400" />
                  ))}
                </div>
                <p className="text-sm text-white/70 mb-4 leading-relaxed">"{t.text}"</p>
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-violet-500/30 flex items-center justify-center text-xs font-bold text-violet-300">
                    {t.avatar}
                  </div>
                  <div>
                    <p className="text-xs font-semibold text-white">{t.name}</p>
                    <p className="text-[10px] text-white/40">{t.role}</p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="py-24 px-6">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-black mb-4">Simple, transparent pricing</h2>
            <p className="text-white/50">14-day free trial. No credit card required. Cancel anytime.</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {PLANS.map((plan, i) => (
              <div
                key={plan.name}
                className={`rounded-2xl p-6 border transition-all ${
                  plan.highlight
                    ? "bg-gradient-to-b from-violet-500/15 to-violet-500/5 border-violet-500/40 relative"
                    : "bg-[#111218] border-white/5"
                }`}
              >
                {plan.highlight && (
                  <Badge className="absolute -top-3 left-1/2 -translate-x-1/2 bg-violet-600 text-white border-0 text-xs">
                    Most Popular
                  </Badge>
                )}
                <p className="text-sm font-bold text-white mb-1">{plan.name}</p>
                <p className="text-xs text-white/40 mb-4">{plan.description}</p>
                <div className="mb-6">
                  <span className="text-4xl font-black text-white">${plan.price}</span>
                  <span className="text-white/40 text-sm">/month</span>
                </div>
                <ul className="space-y-2 mb-6">
                  {plan.features.map((f) => (
                    <li key={f} className="flex items-center gap-2 text-xs text-white/70">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
                      {f}
                    </li>
                  ))}
                </ul>
                <Link href="/register">
                  <Button className={`w-full text-sm ${plan.highlight ? "bg-violet-600 hover:bg-violet-500" : "bg-white/10 hover:bg-white/15 text-white"}`}>
                    {plan.cta}
                  </Button>
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24 px-6">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-5xl font-black mb-6">
            Your competitors are using AI.<br />
            <span className="text-violet-400">Are you?</span>
          </h2>
          <p className="text-white/50 mb-8">
            Join 50,000+ sellers using SellerVision AI to find opportunities, optimize operations,
            and build businesses that grow while they sleep.
          </p>
          <Link href="/register">
            <Button size="lg" className="bg-gradient-to-r from-violet-600 to-blue-600 hover:opacity-90 px-10 h-12 text-sm">
              Start Your Free Trial Today
              <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/5 py-12 px-6">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded bg-gradient-to-br from-violet-500 to-blue-500 flex items-center justify-center">
              <Brain className="w-3.5 h-3.5 text-white" />
            </div>
            <span className="text-sm font-bold text-white">SellerVision AI</span>
          </div>
          <p className="text-xs text-white/25">© 2026 SellerVision AI. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}
