// ── SellerVision AI — Sentry Server (Node.js) Config ─────────────────
// Runs in the Next.js Node runtime (RSC, API routes, server actions).
// https://docs.sentry.io/platforms/javascript/guides/nextjs/

import * as Sentry from "@sentry/nextjs";

const SENTRY_DSN = process.env.NEXT_PUBLIC_SENTRY_DSN;

if (SENTRY_DSN) {
  Sentry.init({
    dsn: SENTRY_DSN,
    environment: process.env.NODE_ENV,
    tracesSampleRate: process.env.NODE_ENV === "production" ? 0.1 : 1.0,

    // Don't include PII in server-side events
    sendDefaultPii: false,

    beforeSend(event) {
      // Drop 401/403/429 — expected in normal auth flows
      const status = (event.contexts?.response as any)?.status_code;
      if (status && [401, 403, 429].includes(status)) return null;
      // Strip auth headers
      if (event.request?.headers) {
        delete (event.request.headers as Record<string, unknown>)["Authorization"];
        delete (event.request.headers as Record<string, unknown>)["X-API-Key"];
      }
      return event;
    },
  });
}
