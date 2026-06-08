"use client";

import { useEffect } from "react";
import * as Sentry from "@sentry/nextjs";
import { AlertTriangle, RefreshCw, Home } from "lucide-react";
import { Button } from "@/components/ui/button";

/**
 * Dashboard-level error boundary.
 * Catches unhandled errors thrown by any (dashboard)/** page or layout
 * without blowing up the entire app shell (unlike app/error.tsx which
 * wraps everything including the root html/body).
 */
export default function DashboardError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    Sentry.captureException(error);
    console.error("[DashboardError]", error);
  }, [error]);

  return (
    <div className="flex-1 flex items-center justify-center p-8 min-h-[60vh]">
      <div className="text-center max-w-sm">
        <div className="w-14 h-14 rounded-2xl bg-red-500/10 border border-red-500/20 flex items-center justify-center mx-auto mb-5">
          <AlertTriangle className="w-7 h-7 text-red-400" />
        </div>

        <h2 className="text-lg font-bold text-white mb-1">Something went wrong</h2>
        <p className="text-sm text-white/40 mb-1 leading-relaxed">
          {error.message || "An unexpected error occurred loading this page."}
        </p>
        {error.digest && (
          <p className="text-[10px] font-mono text-white/20 mb-6">
            Error ID: {error.digest}
          </p>
        )}
        {!error.digest && <div className="mb-6" />}

        <div className="flex items-center justify-center gap-3">
          <Button
            onClick={reset}
            className="bg-violet-600 hover:bg-violet-500"
          >
            <RefreshCw className="w-3.5 h-3.5 mr-1.5" />
            Try again
          </Button>
          <Button
            variant="outline"
            onClick={() => (window.location.href = "/dashboard")}
            className="border-white/10 bg-white/5 text-white/60 hover:text-white"
          >
            <Home className="w-3.5 h-3.5 mr-1.5" />
            Dashboard
          </Button>
        </div>
      </div>
    </div>
  );
}
