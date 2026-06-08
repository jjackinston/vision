"use client";

/**
 * PlanGateGuard — renders a blurred upgrade wall when the tenant's plan is
 * below the required tier.  Wrap any premium UI with this component.
 *
 * Usage
 * -----
 *   <PlanGateGuard requiredPlan="business" feature="Digital Twin">
 *     <DigitalTwinChart />
 *   </PlanGateGuard>
 *
 * Variant without children (standalone gate page/section):
 *   <PlanGateGuard requiredPlan="professional" feature="AI Agents" standalone />
 */

import { ReactNode } from "react";
import { Lock, Zap, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { usePlanGate, PLAN_DISPLAY, PLAN_PRICE, type PlanTier } from "@/hooks/usePlanGate";
import { api } from "@/lib/api";

// ── Feature descriptions used in the upgrade copy ────────────────────────────

const FEATURE_HIGHLIGHTS: Record<string, string[]> = {
  "Digital Twin":         ["What-if scenario modeling", "Revenue & profit forecasting", "Inventory simulations"],
  "AI Agents":            ["Autonomous product research", "Competitor monitoring", "PPC optimization"],
  "PPC Manager":          ["Automated bid management", "Campaign analytics", "Keyword harvesting"],
  "White Label":          ["Custom branding", "Client sub-accounts", "Agency dashboard"],
  "Automation":           ["Rule-based triggers", "Scheduled reports", "Workflow builder"],
  "Competitor Analysis":  ["Real-time price tracking", "Buy Box monitoring", "Seller intelligence"],
};

// ── Component ─────────────────────────────────────────────────────────────────

interface PlanGateGuardProps {
  /** Minimum plan required to see the content. */
  requiredPlan: PlanTier;
  /** Display name of the feature being gated (used in copy). */
  feature: string;
  /** The children to render when the user has access. */
  children?: ReactNode;
  /** When true, renders a full-section gate (no blur, no children expected). */
  standalone?: boolean;
  /** Additional className on the wrapper. */
  className?: string;
}

export function PlanGateGuard({
  requiredPlan,
  feature,
  children,
  standalone = false,
  className,
}: PlanGateGuardProps) {
  const { hasAccess, isLoading, currentPlan, isTrialExpired, isPastDue } =
    usePlanGate(requiredPlan);

  // While loading, render children (or nothing for standalone) — avoids flash
  if (isLoading) {
    return standalone ? null : <>{children}</>;
  }

  // If access is granted, just render children
  if (hasAccess) {
    return <>{children}</>;
  }

  // ── Build upgrade copy ────────────────────────────────────────────────────
  const planDisplay = PLAN_DISPLAY[requiredPlan];
  const planPrice   = PLAN_PRICE[requiredPlan];
  const highlights  = FEATURE_HIGHLIGHTS[feature] ?? [
    "Unlock advanced AI capabilities",
    "Access premium analytics",
    "Priority support",
  ];

  let headlineVerb = `Upgrade to ${planDisplay}`;
  let subline: string;
  if (isPastDue) {
    headlineVerb = "Payment Required";
    subline = "Your subscription is past-due. Update your payment method to restore access.";
  } else if (isTrialExpired) {
    headlineVerb = "Trial Expired";
    subline = `Your free trial has ended. Upgrade to ${planDisplay} to unlock ${feature}.`;
  } else {
    subline = `${feature} is available on the ${planDisplay} plan and above.`;
  }

  const handleUpgrade = async () => {
    try {
      if (isPastDue) {
        const { portal_url } = await api.createPortalSession();
        window.location.href = portal_url;
      } else {
        const { checkout_url } = await api.createCheckoutSession(requiredPlan);
        window.location.href = checkout_url;
      }
    } catch {
      window.location.href = "/settings?section=billing";
    }
  };

  // ── Standalone gate (full section) ────────────────────────────────────────
  if (standalone) {
    return (
      <div className={cn(
        "flex items-center justify-center min-h-[400px] p-8",
        className
      )}>
        <UpgradeCard
          headlineVerb={headlineVerb}
          subline={subline}
          planDisplay={planDisplay}
          planPrice={planPrice}
          feature={feature}
          highlights={highlights}
          isPastDue={isPastDue}
          onUpgrade={handleUpgrade}
        />
      </div>
    );
  }

  // ── Blurred overlay gate ───────────────────────────────────────────────────
  return (
    <div className={cn("relative overflow-hidden rounded-xl", className)}>
      {/* Blurred children underneath */}
      {children && (
        <div className="pointer-events-none select-none blur-sm opacity-40">
          {children}
        </div>
      )}

      {/* Overlay */}
      <div className="absolute inset-0 flex items-center justify-center bg-[#0A0B0E]/70 backdrop-blur-[2px] z-10 rounded-xl">
        <UpgradeCard
          headlineVerb={headlineVerb}
          subline={subline}
          planDisplay={planDisplay}
          planPrice={planPrice}
          feature={feature}
          highlights={highlights}
          isPastDue={isPastDue}
          onUpgrade={handleUpgrade}
          compact
        />
      </div>
    </div>
  );
}

// ── Inner card ─────────────────────────────────────────────────────────────────

interface UpgradeCardProps {
  headlineVerb: string;
  subline: string;
  planDisplay: string;
  planPrice: string;
  feature: string;
  highlights: string[];
  isPastDue: boolean;
  onUpgrade: () => void;
  compact?: boolean;
}

function UpgradeCard({
  headlineVerb,
  subline,
  planDisplay,
  planPrice,
  feature,
  highlights,
  isPastDue,
  onUpgrade,
  compact = false,
}: UpgradeCardProps) {
  return (
    <div className={cn(
      "bg-[#13141A] border border-white/10 rounded-2xl shadow-2xl text-center",
      compact ? "p-6 max-w-sm" : "p-8 max-w-md w-full"
    )}>
      {/* Icon */}
      <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-violet-500/20 to-blue-500/20 border border-violet-500/30 flex items-center justify-center mx-auto mb-4">
        <Lock className="w-5 h-5 text-violet-400" />
      </div>

      {/* Plan badge */}
      <Badge
        variant="outline"
        className="mb-3 bg-violet-500/10 text-violet-300 border-violet-500/30 text-xs"
      >
        {planDisplay} · {planPrice}
      </Badge>

      {/* Headline */}
      <h3 className="text-lg font-bold text-white mb-2">{headlineVerb}</h3>
      <p className="text-sm text-gray-400 mb-5 leading-relaxed">{subline}</p>

      {/* Feature bullets */}
      {!compact && (
        <ul className="text-left mb-6 space-y-2">
          {highlights.map((h) => (
            <li key={h} className="flex items-center gap-2 text-sm text-gray-300">
              <Zap className="w-3.5 h-3.5 text-violet-400 flex-shrink-0" />
              {h}
            </li>
          ))}
        </ul>
      )}

      {/* CTA */}
      <Button
        onClick={onUpgrade}
        className="w-full bg-gradient-to-r from-violet-600 to-blue-600 hover:from-violet-500 hover:to-blue-500 text-white font-semibold"
      >
        {isPastDue ? "Update Payment" : `Upgrade to ${planDisplay}`}
        <ArrowRight className="w-4 h-4 ml-2" />
      </Button>

      <p className="text-[11px] text-gray-600 mt-3">
        Cancel anytime · Instant access
      </p>
    </div>
  );
}
