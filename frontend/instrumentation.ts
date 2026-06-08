// ── Next.js instrumentation hook ────────────────────────────────────
// Loaded once per server process. Registers Sentry for Node + Edge runtimes.
// https://nextjs.org/docs/app/building-your-application/optimizing/instrumentation

export async function register() {
  if (process.env.NEXT_RUNTIME === "nodejs") {
    await import("./sentry.server.config");
  }
  if (process.env.NEXT_RUNTIME === "edge") {
    await import("./sentry.edge.config");
  }
}

// Capture unhandled React errors from App Router
export const onRequestError = async (
  err: unknown,
  request: { path: string; method: string },
  context: { routerKind: string; routePath: string; routeType: string }
) => {
  const Sentry = await import("@sentry/nextjs");
  // Next.js onRequestError provides { path, method }; Sentry's RequestInfo also
  // requires `headers`. We don't have them here so cast to avoid a type error —
  // Sentry handles missing headers gracefully at runtime.
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  Sentry.captureRequestError(err, request as any, context);
};
