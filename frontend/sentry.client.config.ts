// ── SellerVision AI — Sentry Client (browser) Config ─────────────────
// Runs in the user's browser. Captures JS errors + performance + replays.
// https://docs.sentry.io/platforms/javascript/guides/nextjs/

import * as Sentry from "@sentry/nextjs";

const SENTRY_DSN = process.env.NEXT_PUBLIC_SENTRY_DSN;

if (SENTRY_DSN) {
  Sentry.init({
    dsn: SENTRY_DSN,
    environment: process.env.NODE_ENV,

    // ── Performance tracing ──────────────────────────────────────
    // 100% in dev so you can see all traces locally.
    // 10% in production — adjust based on your traffic volume.
    tracesSampleRate: process.env.NODE_ENV === "production" ? 0.1 : 1.0,

    // ── Session Replay ───────────────────────────────────────────
    // Record 5% of all sessions, 100% of sessions that have an error.
    replaysSessionSampleRate: 0.05,
    replaysOnErrorSampleRate: 1.0,

    integrations: [
      Sentry.replayIntegration({
        // Mask all text and block all media by default (GDPR-safe)
        maskAllText: true,
        blockAllMedia: true,
      }),
      Sentry.browserTracingIntegration(),
    ],

    // ── Noise filtering ──────────────────────────────────────────
    ignoreErrors: [
      // Network errors (user went offline, request cancelled)
      "Network request failed",
      "NetworkError",
      "Failed to fetch",
      "Load failed",
      // Browser extensions injecting errors
      /extensions\//i,
      /^chrome:\/\//i,
      /^safari-extension:\/\//i,
      // ResizeObserver benign loop
      "ResizeObserver loop limit exceeded",
      "ResizeObserver loop completed with undelivered notifications",
    ],

    beforeSend(event) {
      // Strip auth tokens from request headers in Sentry payloads
      if (event.request?.headers) {
        delete (event.request.headers as Record<string, unknown>)["Authorization"];
        delete (event.request.headers as Record<string, unknown>)["X-API-Key"];
      }
      return event;
    },
  });
}
