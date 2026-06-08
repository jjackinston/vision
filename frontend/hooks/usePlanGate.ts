"use client";

/**
 * usePlanGate — check whether the current tenant has access to a feature
 * based on their plan tier.
 *
 * Usage
 * -----
 *   const { hasAccess, isLoading, requiredPlan } = usePlanGate("business");
 *
 *   if (!hasAccess) return <PlanGateGuard requiredPlan="business" feature="Digital Twin" />;
 */

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

// ── Plan tier ordering (must match backend PLAN_TIERS) ───────────────────────

export type PlanTier = "starter" | "professional" | "business" | "agency" | "enterprise";

export const PLAN_TIERS: Record<PlanTier, number> = {
  starter:      0,
  professional: 1,
  business:     2,
  agency:       3,
  enterprise:   4,
};

export const PLAN_DISPLAY: Record<PlanTier, string> = {
  starter:      "Starter",
  professional: "Professional",
  business:     "Business",
  agency:       "Agency",
  enterprise:   "Enterprise",
};

export const PLAN_PRICE: Record<PlanTier, string> = {
  starter:      "$49/mo",
  professional: "$149/mo",
  business:     "$299/mo",
  agency:       "$599/mo",
  enterprise:   "Custom",
};

// ── Hook ─────────────────────────────────────────────────────────────────────

export interface PlanGateResult {
  /** Whether the tenant's current plan is at or above `requiredPlan`. */
  hasAccess: boolean;
  /** The tenant's current plan name (lowercased). */
  currentPlan: PlanTier;
  /** The plan that was checked against. */
  requiredPlan: PlanTier;
  /** True while the subscription query is in-flight. */
  isLoading: boolean;
  /** True when the trial has expired with no paid subscription. */
  isTrialExpired: boolean;
  /** True when the subscription is past-due (payment failed). */
  isPastDue: boolean;
}

export function usePlanGate(requiredPlan: PlanTier): PlanGateResult {
  const { data, isLoading } = useQuery({
    queryKey: ["subscription"],
    queryFn: () => api.getSubscription(),
    staleTime: 1000 * 60 * 5, // 5 min
    retry: false,
  });

  const sub = data as any;

  // Normalise the plan name from the API response
  const rawPlan = (sub?.plan ?? "starter").toLowerCase() as PlanTier;
  const currentPlan: PlanTier = rawPlan in PLAN_TIERS ? rawPlan : "starter";

  const currentTier = PLAN_TIERS[currentPlan];
  const requiredTier = PLAN_TIERS[requiredPlan];

  // Trial-expired: no stripe subscription + trial_end in the past
  const isTrialExpired =
    !sub?.stripe_subscription_id &&
    sub?.trial_end != null &&
    sub.trial_end * 1000 < Date.now();

  // Past-due: Stripe status is 'past_due' or 'unpaid'
  const isPastDue =
    sub?.status === "past_due" || sub?.status === "unpaid";

  const hasAccess =
    !isLoading &&
    !isTrialExpired &&
    !isPastDue &&
    currentTier >= requiredTier;

  return {
    hasAccess,
    currentPlan,
    requiredPlan,
    isLoading,
    isTrialExpired,
    isPastDue,
  };
}

// ── Convenience wrapper ───────────────────────────────────────────────────────

/** Returns true if the tenant is on the given plan or any higher tier. */
export function useHasPlan(minPlan: PlanTier): boolean {
  const { hasAccess } = usePlanGate(minPlan);
  return hasAccess;
}
