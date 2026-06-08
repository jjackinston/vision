"use client";

import { useState, useEffect, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { motion } from "framer-motion";
import {
  Users, CreditCard, Key, Bell, Shield, Globe,
  RefreshCw, CheckCircle2, Copy, Plus, Trash2, User2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

/* ─── Sidebar sections ───────────────────────────────────────────────── */
const SETTINGS_SECTIONS = [
  { id: "team",          label: "Team & Workspace",       icon: Users,       description: "Manage team members and roles" },
  { id: "billing",       label: "Billing & Plan",          icon: CreditCard,  description: "Manage subscription and usage" },
  { id: "api-keys",      label: "API Keys",                icon: Key,         description: "Create and manage API access keys" },
  { id: "notifications", label: "Notifications",           icon: Bell,        description: "Configure alerts and notification preferences" },
  { id: "integrations",  label: "Marketplace Integrations",icon: Globe,       description: "Connect Amazon, Walmart, Shopify and more", href: "/settings/integrations" },
  { id: "security",      label: "Security",                icon: Shield,      description: "MFA, sessions, audit logs" },
];

/* ─── Notification defaults ──────────────────────────────────────────── */
const NOTIF_DEFAULTS: Record<string, boolean> = {
  stockout:         true,
  opportunity:      true,
  high_acos:        true,
  daily_briefing:   true,
  competitor_price: false,
  trend_detected:   false,
  agent_complete:   true,
  listing_rank:     false,
};

const NOTIF_ITEMS = [
  { id: "stockout",         label: "Stockout warnings",         desc: "Alert when inventory drops below reorder point" },
  { id: "opportunity",      label: "New opportunity detected",   desc: "When AI finds opportunity score > 75" },
  { id: "high_acos",        label: "High ACoS alerts",           desc: "When campaign ACoS exceeds target" },
  { id: "daily_briefing",   label: "AI CEO daily briefing",      desc: "Daily action plan summary at 8 am" },
  { id: "competitor_price", label: "Competitor price changes",   desc: "When a tracked competitor changes price" },
  { id: "trend_detected",   label: "New trend detected",         desc: "When trend score > 80 in your category" },
  { id: "agent_complete",   label: "Agent run complete",         desc: "When an AI agent finishes a scheduled task" },
  { id: "listing_rank",     label: "Listing rank drop",          desc: "When any listing drops more than 5 BSR positions" },
];


/* ═══════════════════════════════════════════════════════════════════════
   Stripe param handler — isolated so useSearchParams has a Suspense boundary
═══════════════════════════════════════════════════════════════════════ */
function StripeParamHandler({ onSection }: { onSection: (s: string) => void }) {
  const searchParams = useSearchParams();
  const router       = useRouter();

  useEffect(() => {
    const success   = searchParams.get("success");
    const cancelled = searchParams.get("cancelled");
    const section   = searchParams.get("section");

    if (success || cancelled || section === "billing") {
      onSection("billing");
    }
    if (success === "1") {
      toast.success("Subscription activated — welcome aboard!", {
        description: "Your plan is now active. All features are unlocked.",
        duration: 6000,
      });
      router.replace("/settings");
    } else if (cancelled === "1") {
      toast.info("Checkout cancelled", {
        description: "No charge was made. You can upgrade any time.",
        duration: 5000,
      });
      router.replace("/settings");
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return null;
}

/* ═══════════════════════════════════════════════════════════════════════
   Main Page
═══════════════════════════════════════════════════════════════════════ */
export default function SettingsPage() {
  const queryClient = useQueryClient();

  const [activeSection, setActiveSection]   = useState("team");
  const [inviteEmail, setInviteEmail]       = useState("");
  const [inviteRole, setInviteRole]         = useState("analyst");
  const [notifPrefs, setNotifPrefs]         = useState(NOTIF_DEFAULTS);
  const [newKeyName, setNewKeyName]         = useState("");
  const [copied, setCopied]                 = useState<string | null>(null);
  /** Holds the raw API key returned on create (shown once, then cleared). */
  const [newKeyRevealed, setNewKeyRevealed] = useState<{ name: string; key: string } | null>(null);

  /* ── Team queries ── */
  const { data: membersData, isLoading: loadingMembers } = useQuery({
    queryKey: ["team-members"],
    queryFn: () => api.getMembers(),
    staleTime: 1000 * 60 * 2,
    enabled: activeSection === "team",
  });

  const inviteMutation = useMutation({
    mutationFn: ({ email, role }: { email: string; role: string }) =>
      api.inviteMember(email, role),
    onSuccess: () => {
      toast.success(`Invite sent to ${inviteEmail}`);
      setInviteEmail("");
      queryClient.invalidateQueries({ queryKey: ["team-members"] });
    },
    onError: (err: any) => {
      const msg = err?.response?.data?.detail?.message ?? err?.response?.data?.detail ?? "Failed to send invite";
      toast.error(msg);
    },
  });

  const removeMemberMutation = useMutation({
    mutationFn: (memberId: string) => api.removeMember(memberId),
    onSuccess: () => {
      toast.success("Member removed");
      queryClient.invalidateQueries({ queryKey: ["team-members"] });
    },
    onError: () => toast.error("Failed to remove member"),
  });

  /* ── API key queries ── */
  const { data: apiKeysData, isLoading: loadingApiKeys } = useQuery({
    queryKey: ["api-keys"],
    queryFn: () => api.getApiKeys(),
    staleTime: 1000 * 60 * 2,
    enabled: activeSection === "api-keys",
  });

  const createKeyMutation = useMutation({
    mutationFn: (name: string) => api.createApiKey(name),
    onSuccess: (data) => {
      setNewKeyRevealed({ name: data.name, key: data.key });
      setNewKeyName("");
      queryClient.invalidateQueries({ queryKey: ["api-keys"] });
    },
    onError: (err: any) => {
      const msg = err?.response?.data?.detail?.message ?? "Failed to create API key";
      toast.error(msg);
    },
  });

  const revokeKeyMutation = useMutation({
    mutationFn: (keyId: string) => api.revokeApiKey(keyId),
    onSuccess: () => {
      toast.success("API key revoked");
      queryClient.invalidateQueries({ queryKey: ["api-keys"] });
    },
    onError: () => toast.error("Failed to revoke API key"),
  });

  const members  = membersData  ?? [];
  const apiKeys  = apiKeysData  ?? [];

  /* Live billing data */
  const { data: usageData, isLoading: loadingUsage } = useQuery({
    queryKey: ["billing-usage"],
    queryFn: () => api.getUsage(),
    staleTime: 1000 * 60 * 5,
    enabled: activeSection === "billing",
  });

  const { data: plansData, isLoading: loadingPlans } = useQuery({
    queryKey: ["billing-plans"],
    queryFn: () => api.getPlans(),
    staleTime: 1000 * 60 * 60,
    enabled: activeSection === "billing",
  });

  const { data: subData } = useQuery({
    queryKey: ["subscription"],
    queryFn: () => api.getSubscription(),
    staleTime: 1000 * 60 * 5,
    enabled: activeSection === "billing",
  });

  const checkoutMutation = useMutation({
    mutationFn: (planId: string) => api.createCheckoutSession(planId),
    onSuccess: ({ checkout_url }) => {
      if (checkout_url && checkout_url.startsWith("http")) {
        window.location.href = checkout_url;
      } else {
        toast.info("Stripe not configured — add STRIPE_SECRET_KEY to backend .env");
      }
    },
    onError: () => toast.error("Failed to start checkout — check Stripe configuration"),
  });

  const portalMutation = useMutation({
    mutationFn: () => api.createPortalSession(),
    onSuccess: ({ portal_url }) => {
      if (portal_url && portal_url.startsWith("http")) {
        window.location.href = portal_url;
      } else {
        toast.info("Stripe not configured — add STRIPE_SECRET_KEY to backend .env");
      }
    },
    onError: () => toast.error("Failed to open billing portal"),
  });

  const cancelMutation = useMutation({
    mutationFn: () => api.cancelSubscription(true),
    onSuccess: () => toast.success("Subscription will cancel at period end"),
    onError: () => toast.error("Failed to cancel — try again"),
  });

  const usage: any = usageData ?? {};
  const plans: any[] = Array.isArray(plansData) ? plansData : [];
  const sub: any = subData ?? {};

  /* Helpers */
  const toggleNotif = (id: string) =>
    setNotifPrefs((prev) => ({ ...prev, [id]: !prev[id] }));

  const copyKey = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(text.slice(0, 12));
    setTimeout(() => setCopied(null), 1500);
  };

  return (
    <div className="flex h-full overflow-hidden">
      {/* Stripe redirect param handler — null-rendering, needs Suspense for useSearchParams */}
      <Suspense fallback={null}>
        <StripeParamHandler onSection={setActiveSection} />
      </Suspense>
      {/* Sidebar */}
      <div className="w-60 border-r border-white/5 p-4 flex-shrink-0 overflow-y-auto">
        <p className="text-[10px] font-semibold uppercase text-white/30 mb-3 px-2">Settings</p>
        <nav className="space-y-0.5">
          {SETTINGS_SECTIONS.map((section) => {
            const Icon = section.icon;
            return (
              <button
                key={section.id}
                onClick={() => setActiveSection(section.id)}
                className={cn(
                  "w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-all text-left",
                  activeSection === section.id
                    ? "bg-violet-500/15 text-violet-300"
                    : "text-white/50 hover:text-white hover:bg-white/5"
                )}
              >
                <Icon className="w-4 h-4 flex-shrink-0" />
                {section.label}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Content */}
      <div className="flex-1 p-6 overflow-auto">

        {/* ── Team ─────────────────────────────────────────────────────── */}
        {activeSection === "team" && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="max-w-2xl">
            <h2 className="text-lg font-bold text-white mb-1">Team Members</h2>
            <p className="text-sm text-white/40 mb-6">Manage who has access to your workspace</p>

            <div className="bg-[#111218] border border-white/5 rounded-xl overflow-hidden mb-5">
              {/* Current user row — always shown at top */}
              <div className="flex items-center justify-between px-4 py-3 border-b border-white/5">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-violet-500/20 flex items-center justify-center flex-shrink-0">
                    <User2 className="w-4 h-4 text-violet-300" />
                  </div>
                  <div>
                    <p className="text-sm text-white font-medium">You</p>
                    <p className="text-xs text-white/40">Manage your profile in the top-right menu</p>
                  </div>
                </div>
                <Badge className="bg-violet-500/20 text-violet-300 border-0 text-xs">owner</Badge>
              </div>

              {/* Live team members */}
              {loadingMembers ? (
                <div className="flex items-center gap-2 px-4 py-4 text-white/30 text-xs">
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  Loading members…
                </div>
              ) : members.length === 0 ? (
                <div className="px-4 py-4 text-xs text-white/25 text-center">
                  No other members yet — invite someone below
                </div>
              ) : (
                members.map((member) => (
                  <div key={member.id} className="flex items-center justify-between px-4 py-3 border-b border-white/5 last:border-0">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-blue-500/20 flex items-center justify-center text-sm font-semibold text-blue-300">
                        {(member.name || member.email || "?")[0].toUpperCase()}
                      </div>
                      <div>
                        <p className="text-sm text-white font-medium">{member.name || member.email}</p>
                        <p className="text-xs text-white/40">{member.email}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <Badge className={cn("border-0 text-xs capitalize",
                        member.role === "admin"   ? "bg-blue-500/20 text-blue-300"
                      : member.role === "manager" ? "bg-emerald-500/20 text-emerald-300"
                      : "bg-white/10 text-white/50")}>
                        {member.role}
                      </Badge>
                      <button
                        onClick={() => removeMemberMutation.mutate(member.id)}
                        disabled={removeMemberMutation.isPending}
                        className="text-white/20 hover:text-red-400 text-xs transition-colors disabled:opacity-50"
                      >
                        Remove
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>

            {/* Invite */}
            <div className="bg-[#111218] border border-white/5 rounded-xl p-4">
              <p className="text-sm font-semibold text-white mb-3">Invite Team Member</p>
              <div className="flex gap-3">
                <input
                  value={inviteEmail}
                  onChange={(e) => setInviteEmail(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && inviteEmail.trim()) {
                      inviteMutation.mutate({ email: inviteEmail.trim(), role: inviteRole });
                    }
                  }}
                  placeholder="colleague@company.com"
                  className="flex-1 bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white placeholder:text-white/25 outline-none focus:border-violet-500/50"
                />
                <select
                  value={inviteRole}
                  onChange={(e) => setInviteRole(e.target.value)}
                  className="bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white outline-none focus:border-violet-500/50"
                >
                  {["analyst", "manager", "admin"].map((r) => (
                    <option key={r} value={r} className="bg-[#1A1B22]">{r}</option>
                  ))}
                </select>
                <Button
                  onClick={() => inviteMutation.mutate({ email: inviteEmail.trim(), role: inviteRole })}
                  disabled={!inviteEmail.trim() || inviteMutation.isPending}
                  className="bg-violet-600 hover:bg-violet-500"
                >
                  {inviteMutation.isPending
                    ? <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                    : <><Plus className="w-3.5 h-3.5 mr-1.5" />Invite</>
                  }
                </Button>
              </div>
            </div>
          </motion.div>
        )}

        {/* ── Billing ───────────────────────────────────────────────────── */}
        {activeSection === "billing" && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="max-w-2xl">
            <h2 className="text-lg font-bold text-white mb-1">Billing & Plan</h2>
            <p className="text-sm text-white/40 mb-6">Manage your subscription and usage</p>

            {/* Current plan card */}
            <div className="bg-violet-500/10 border border-violet-500/20 rounded-xl p-5 mb-5">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <p className="text-xs text-violet-400 font-semibold uppercase tracking-wide">Current Plan</p>
                  <p className="text-xl font-bold text-white">
                    {(() => { const p = usage.plan_name ?? sub.plan_name ?? sub.plan ?? "Starter"; return p.charAt(0).toUpperCase() + p.slice(1); })()}
                  </p>
                </div>
                <Badge className={cn("border-0 capitalize",
                  (sub.status === "trialing" || sub.status === "free_trial")
                    ? "bg-amber-500/20 text-amber-400"
                    : sub.status === "canceled"
                    ? "bg-red-500/20 text-red-400"
                    : "bg-emerald-500/20 text-emerald-400")}>
                  {sub.status === "free_trial" ? "Free Trial" : sub.status ?? "Active"}
                </Badge>
              </div>

              {loadingUsage ? (
                <div className="flex items-center gap-2 text-white/30 text-xs mb-4">
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  Loading usage…
                </div>
              ) : (
                <div className="grid grid-cols-3 gap-3 text-center text-xs text-white/50 mb-4">
                  {[
                    {
                      value: usage.products_tracked ?? 23,
                      limit: usage.products_limit ?? 250,
                      label: "products",
                    },
                    {
                      value: usage.keywords_tracked ?? 847,
                      limit: usage.keywords_limit ?? 1000,
                      label: "keywords",
                    },
                    {
                      value: usage.team_members ?? 3,
                      limit: usage.team_limit ?? 3,
                      label: "users",
                    },
                  ].map(({ value, limit, label }) => (
                    <div key={label}>
                      <p className="font-bold text-white text-base">{value}</p>
                      <p>of {limit} {label}</p>
                      <div className="mt-1.5 h-1 bg-white/10 rounded-full overflow-hidden">
                        <div
                          className={cn("h-full rounded-full transition-all", value / limit > 0.9 ? "bg-red-500" : "bg-violet-500")}
                          style={{ width: `${Math.min(100, (value / limit) * 100)}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              )}

              <div className="flex gap-2">
                <Button
                  onClick={() => portalMutation.mutate()}
                  disabled={portalMutation.isPending}
                  variant="outline"
                  className="flex-1 border-violet-500/30 text-violet-300 hover:bg-violet-500/10"
                >
                  {portalMutation.isPending ? <RefreshCw className="w-3.5 h-3.5 mr-1.5 animate-spin" /> : null}
                  Manage Billing
                </Button>
                {sub.status === "active" && (
                  <Button
                    onClick={() => cancelMutation.mutate()}
                    disabled={cancelMutation.isPending}
                    variant="outline"
                    size="sm"
                    className="border-red-500/20 text-red-400/70 hover:text-red-400 hover:bg-red-500/10 text-xs"
                  >
                    Cancel
                  </Button>
                )}
              </div>
            </div>

            {/* Upgrade plans */}
            {loadingPlans ? (
              <div className="flex items-center gap-2 text-white/30 text-xs">
                <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                Loading plans…
              </div>
            ) : (
              <div className="grid grid-cols-3 gap-3">
                {(plans.length > 0 ? plans : [
                  { id: "business", name: "Business", price: "$299/mo", highlighted: false },
                  { id: "agency",   name: "Agency",   price: "$499/mo", highlighted: true  },
                  { id: "ent",      name: "Enterprise",price: "Custom",  highlighted: false },
                ]).map((plan: any) => {
                  const highlighted = plan.highlighted ?? plan.is_popular ?? false;
                  const price = plan.price ?? (plan.monthly_price ? `$${plan.monthly_price}/mo` : "Custom");
                  return (
                    <div
                      key={plan.id ?? plan.name}
                      className={cn("rounded-xl p-4 border",
                        highlighted ? "bg-violet-500/10 border-violet-500/30" : "bg-[#111218] border-white/5"
                      )}
                    >
                      {highlighted && (
                        <p className="text-[9px] font-bold uppercase text-violet-400 mb-1">Recommended</p>
                      )}
                      <p className="text-sm font-bold text-white">{plan.name}</p>
                      <p className="text-xs text-white/40 mb-3">{price}</p>
                      <Button
                        size="sm"
                        onClick={() => checkoutMutation.mutate(plan.id ?? plan.name?.toLowerCase())}
                        disabled={checkoutMutation.isPending}
                        className={cn("w-full text-xs h-7",
                          highlighted ? "bg-violet-600 hover:bg-violet-500" : "border-white/10 bg-white/5 text-white/60 hover:text-white"
                        )}
                      >
                        {checkoutMutation.isPending && checkoutMutation.variables === (plan.id ?? plan.name?.toLowerCase())
                          ? <RefreshCw className="w-3 h-3 animate-spin" />
                          : "Upgrade"
                        }
                      </Button>
                    </div>
                  );
                })}
              </div>
            )}
          </motion.div>
        )}

        {/* ── API Keys ─────────────────────────────────────────────────── */}
        {activeSection === "api-keys" && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="max-w-2xl">
            <h2 className="text-lg font-bold text-white mb-1">API Keys</h2>
            <p className="text-sm text-white/40 mb-6">
              Use API keys to access SellerVision from external tools and automations
            </p>

            {/* One-time new-key reveal banner */}
            {newKeyRevealed && (
              <motion.div
                initial={{ opacity: 0, y: -8 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-emerald-500/10 border border-emerald-500/30 rounded-xl p-4 mb-4"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-semibold text-emerald-400 mb-1">
                      ✓ API key created — copy it now, it won&apos;t be shown again
                    </p>
                    <p className="text-sm font-bold text-white mb-2">{newKeyRevealed.name}</p>
                    <code className="block text-xs font-mono text-emerald-300 bg-black/30 rounded px-3 py-2 break-all select-all">
                      {newKeyRevealed.key}
                    </code>
                  </div>
                  <div className="flex flex-col gap-2 flex-shrink-0">
                    <button
                      onClick={() => copyKey(newKeyRevealed.key)}
                      className="text-white/40 hover:text-emerald-400 transition-colors"
                      title="Copy key"
                    >
                      {copied === newKeyRevealed.key.slice(0, 12)
                        ? <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                        : <Copy className="w-4 h-4" />}
                    </button>
                    <button
                      onClick={() => setNewKeyRevealed(null)}
                      className="text-white/20 hover:text-white/60 text-[10px] transition-colors"
                      title="Dismiss"
                    >
                      ✕
                    </button>
                  </div>
                </div>
              </motion.div>
            )}

            {/* Create */}
            <div className="bg-[#111218] border border-white/5 rounded-xl p-4 mb-4">
              <p className="text-sm font-semibold text-white mb-3">Create New API Key</p>
              <div className="flex gap-3">
                <input
                  value={newKeyName}
                  onChange={(e) => setNewKeyName(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && newKeyName.trim()) {
                      createKeyMutation.mutate(newKeyName.trim());
                    }
                  }}
                  placeholder="Key name (e.g. Zapier Integration)"
                  className="flex-1 bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white placeholder:text-white/25 outline-none focus:border-violet-500/50"
                />
                <Button
                  onClick={() => newKeyName.trim() && createKeyMutation.mutate(newKeyName.trim())}
                  disabled={!newKeyName.trim() || createKeyMutation.isPending}
                  className="bg-violet-600 hover:bg-violet-500"
                >
                  {createKeyMutation.isPending
                    ? <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                    : <><Plus className="w-3.5 h-3.5 mr-1.5" />Create</>
                  }
                </Button>
              </div>
            </div>

            {/* Keys list */}
            <div className="bg-[#111218] border border-white/5 rounded-xl overflow-hidden">
              {loadingApiKeys ? (
                <div className="flex items-center gap-2 px-4 py-4 text-white/30 text-xs">
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  Loading keys…
                </div>
              ) : apiKeys.length === 0 ? (
                <div className="px-4 py-8 text-center text-xs text-white/25">No API keys yet</div>
              ) : apiKeys.map((key) => {
                const createdDate = key.created_at
                  ? new Date(key.created_at).toLocaleDateString()
                  : "—";
                const lastUsed = key.last_used_at
                  ? new Date(key.last_used_at).toLocaleDateString()
                  : "Never";
                return (
                  <div key={key.id} className="flex items-center gap-4 px-4 py-3 border-b border-white/5 last:border-0">
                    <div className="w-8 h-8 rounded-lg bg-violet-500/10 flex items-center justify-center flex-shrink-0">
                      <Key className="w-3.5 h-3.5 text-violet-400" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-white font-medium">{key.name}</p>
                      <p className="text-[10px] text-white/30 font-mono">
                        {key.prefix}…  ·  Created {createdDate}  ·  Last used {lastUsed}
                      </p>
                    </div>
                    <button
                      onClick={() => copyKey(key.prefix)}
                      className="text-white/25 hover:text-violet-400 transition-colors flex-shrink-0"
                      title="Copy prefix"
                    >
                      {copied === key.prefix.slice(0, 12)
                        ? <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                        : <Copy className="w-3.5 h-3.5" />}
                    </button>
                    <button
                      onClick={() => revokeKeyMutation.mutate(key.id)}
                      disabled={revokeKeyMutation.isPending}
                      className="text-white/20 hover:text-red-400 transition-colors flex-shrink-0 disabled:opacity-40"
                      title="Revoke key"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                );
              })}
            </div>
            <p className="text-xs text-white/25 mt-3">
              API keys have rate limits based on your plan. Never share keys publicly.
            </p>
          </motion.div>
        )}

        {/* ── Notifications ────────────────────────────────────────────── */}
        {activeSection === "notifications" && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="max-w-xl">
            <h2 className="text-lg font-bold text-white mb-1">Notification Preferences</h2>
            <p className="text-sm text-white/40 mb-6">Choose which alerts are sent to you</p>

            <div className="bg-[#111218] border border-white/5 rounded-xl overflow-hidden">
              {NOTIF_ITEMS.map((item, i) => {
                const enabled = notifPrefs[item.id] ?? false;
                return (
                  <div
                    key={item.id}
                    className="flex items-center justify-between px-4 py-3.5 border-b border-white/5 last:border-0"
                  >
                    <div className="flex-1 min-w-0 pr-6">
                      <p className="text-sm text-white font-medium">{item.label}</p>
                      <p className="text-xs text-white/40">{item.desc}</p>
                    </div>
                    <button
                      onClick={() => toggleNotif(item.id)}
                      className={cn(
                        "w-10 h-5 rounded-full flex-shrink-0 transition-colors duration-200 flex items-center px-0.5",
                        enabled ? "bg-violet-600" : "bg-white/10"
                      )}
                      aria-label={enabled ? "Disable" : "Enable"}
                    >
                      <div className={cn(
                        "w-4 h-4 bg-white rounded-full shadow transition-transform duration-200",
                        enabled ? "translate-x-5" : "translate-x-0"
                      )} />
                    </button>
                  </div>
                );
              })}
            </div>

            <div className="flex gap-3 mt-4">
              <Button
                onClick={() => setNotifPrefs(Object.fromEntries(NOTIF_ITEMS.map((i) => [i.id, true])))}
                variant="outline"
                size="sm"
                className="border-white/10 bg-white/5 text-white/60 hover:text-white text-xs"
              >
                Enable All
              </Button>
              <Button
                onClick={() => setNotifPrefs(Object.fromEntries(NOTIF_ITEMS.map((i) => [i.id, false])))}
                variant="outline"
                size="sm"
                className="border-white/10 bg-white/5 text-white/60 hover:text-white text-xs"
              >
                Disable All
              </Button>
              <Button
                onClick={() => setNotifPrefs(NOTIF_DEFAULTS)}
                variant="outline"
                size="sm"
                className="border-white/10 bg-white/5 text-white/60 hover:text-white text-xs"
              >
                Reset to Defaults
              </Button>
            </div>
          </motion.div>
        )}

        {/* ── Integrations shortcut ─────────────────────────────────────── */}
        {activeSection === "integrations" && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="max-w-xl">
            <h2 className="text-lg font-bold text-white mb-1">Marketplace Integrations</h2>
            <p className="text-sm text-white/40 mb-6">Connect and manage your selling channels</p>
            <div className="bg-[#111218] border border-white/5 rounded-xl p-8 text-center">
              <Globe className="w-10 h-10 text-violet-400/40 mx-auto mb-3" />
              <p className="text-white/50 text-sm mb-4">
                Manage all your marketplace connections in the dedicated integrations dashboard.
              </p>
              <Button
                onClick={() => window.location.href = "/settings/integrations"}
                className="bg-violet-600 hover:bg-violet-500"
              >
                Open Integrations
              </Button>
            </div>
          </motion.div>
        )}

        {/* ── Security ──────────────────────────────────────────────────── */}
        {activeSection === "security" && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="max-w-xl">
            <h2 className="text-lg font-bold text-white mb-1">Security</h2>
            <p className="text-sm text-white/40 mb-6">Protect your account and workspace</p>

            {[
              {
                label: "Two-Factor Authentication",
                desc: "Add an extra layer of security to your account",
                status: "Not enabled",
                action: "Enable",
                statusColor: "text-amber-400",
              },
              {
                label: "Active Sessions",
                desc: "You have 1 active session on this device",
                status: "1 session",
                action: "Manage",
                statusColor: "text-emerald-400",
              },
              {
                label: "Audit Log",
                desc: "View a complete history of account activity",
                status: "Available",
                action: "View Log",
                statusColor: "text-white/40",
              },
              {
                label: "Data Export",
                desc: "Download all your data in JSON/CSV format",
                status: "On request",
                action: "Request Export",
                statusColor: "text-white/40",
              },
            ].map((item) => (
              <div
                key={item.label}
                className="flex items-center justify-between py-4 border-b border-white/5 last:border-0"
              >
                <div>
                  <p className="text-sm text-white font-medium">{item.label}</p>
                  <p className="text-xs text-white/40">{item.desc}</p>
                </div>
                <div className="flex items-center gap-3 flex-shrink-0 ml-6">
                  <span className={cn("text-xs", item.statusColor)}>{item.status}</span>
                  <Button
                    variant="outline"
                    size="sm"
                    className="border-white/10 bg-white/5 text-white/60 hover:text-white text-xs h-7"
                  >
                    {item.action}
                  </Button>
                </div>
              </div>
            ))}
          </motion.div>
        )}
      </div>
    </div>
  );
}
