"use client";

/**
 * Registers /sw.js once on mount. No-op in SSR and when SW is unsupported.
 * Placed in the root layout so it runs on every page.
 */

import { useEffect } from "react";

export function ServiceWorkerRegistrar() {
  useEffect(() => {
    if (typeof window === "undefined") return;
    if (!("serviceWorker" in navigator)) return;
    if (process.env.NODE_ENV !== "production") return; // skip in dev

    navigator.serviceWorker
      .register("/sw.js", { scope: "/" })
      .then((reg) => {
        console.log("[SW] registered, scope:", reg.scope);
        // Check for updates once per hour
        setInterval(() => reg.update(), 3_600_000);
      })
      .catch((err) => console.warn("[SW] registration failed:", err));
  }, []);

  return null;
}
