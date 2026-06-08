"use client";

/**
 * /settings/billing — redirect shim
 *
 * Stripe sends the user here after Checkout (success/cancelled) and after the
 * Customer Portal. We forward them to /settings with the same query params so
 * the Settings page can pick them up and show the appropriate toast.
 */

import { Suspense, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";

function BillingRedirectInner() {
  const router = useRouter();
  const params = useSearchParams();

  useEffect(() => {
    const qs = params.toString();
    router.replace(qs ? `/settings?${qs}` : "/settings");
  }, [router, params]);

  return (
    <div className="flex h-full items-center justify-center">
      <div className="flex items-center gap-2 text-white/30 text-sm">
        <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
        </svg>
        Redirecting…
      </div>
    </div>
  );
}

export default function SettingsBillingRedirect() {
  return (
    <Suspense fallback={null}>
      <BillingRedirectInner />
    </Suspense>
  );
}
