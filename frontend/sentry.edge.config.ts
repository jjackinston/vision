// ── SellerVision AI — Sentry Edge Runtime Config ─────────────────────
// Runs in Next.js Edge runtime (middleware, edge API routes).
// Subset of Sentry features available here (no Node.js APIs).

import * as Sentry from "@sentry/nextjs";

const SENTRY_DSN = process.env.NEXT_PUBLIC_SENTRY_DSN;

if (SENTRY_DSN) {
  Sentry.init({
    dsn: SENTRY_DSN,
    environment: process.env.NODE_ENV,
    tracesSampleRate: process.env.NODE_ENV === "production" ? 0.1 : 1.0,
  });
}
