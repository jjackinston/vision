"use client";

import { useEffect } from "react";
import { AlertTriangle, RefreshCw, Home } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("[GlobalError]", error);
  }, [error]);

  return (
    <html>
      <body className="bg-[#0D0E13] min-h-screen flex items-center justify-center p-8">
        <div className="text-center max-w-md">
          <div className="w-16 h-16 rounded-2xl bg-red-500/10 flex items-center justify-center mx-auto mb-6">
            <AlertTriangle className="w-8 h-8 text-red-400" />
          </div>
          <h1 className="text-2xl font-bold text-white mb-2">Something went wrong</h1>
          <p className="text-white/40 text-sm mb-8">
            {error.message || "An unexpected error occurred. Our team has been notified."}
            {error.digest && (
              <span className="block mt-1 font-mono text-xs text-white/20">
                Error ID: {error.digest}
              </span>
            )}
          </p>
          <div className="flex gap-3 justify-center">
            <Button
              onClick={reset}
              className="bg-violet-600 hover:bg-violet-500"
            >
              <RefreshCw className="w-3.5 h-3.5 mr-1.5" />
              Try Again
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
      </body>
    </html>
  );
}
