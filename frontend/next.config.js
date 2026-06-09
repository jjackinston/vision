// @ts-check
const { withSentryConfig } = require("@sentry/nextjs");

/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "standalone",
  // Required for Sentry instrumentation hook (Next.js 14+)
  experimental: {
    instrumentationHook: true,
  },
  // jspdf / html2canvas are browser-only libs. Alias them to false on the
  // server so webpack never bundles their Node.js builds during SSR / SSG.
  webpack: (config, { isServer }) => {
    if (isServer) {
      config.resolve.alias = {
        ...config.resolve.alias,
        jspdf:        false,
        html2canvas:  false,
        canvg:        false,
      };
    }
    return config;
  },
  images: {
    domains: ["images-na.ssl-images-amazon.com", "m.media-amazon.com", "cdn.shopify.com"],
    formats: ["image/avif", "image/webp"],
  },
  headers: async () => [
    {
      source: "/(.*)",
      headers: [
        { key: "X-Content-Type-Options", value: "nosniff" },
        { key: "X-Frame-Options", value: "DENY" },
        { key: "X-XSS-Protection", value: "1; mode=block" },
        { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
        { key: "Strict-Transport-Security", value: "max-age=31536000; includeSubDomains; preload" },
        // Restrict access to browser APIs that SellerVision doesn't need
        {
          key: "Permissions-Policy",
          value: [
            "camera=()",
            "microphone=()",
            "geolocation=()",
            "payment=(self)",      // allow Stripe payment request API
            "usb=()",
            "bluetooth=()",
            "magnetometer=()",
            "gyroscope=()",
            "accelerometer=()",
          ].join(", "),
        },
      ],
    },
    {
      // Allow the service worker to control the entire origin
      source: "/sw.js",
      headers: [
        { key: "Service-Worker-Allowed", value: "/" },
        { key: "Cache-Control", value: "no-cache, no-store, must-revalidate" },
        { key: "Content-Type", value: "application/javascript; charset=utf-8" },
      ],
    },
  ],
};

// ── Sentry build-time config ──────────────────────────────────────────
// Source maps are uploaded to Sentry during `next build` so stack traces
// in production show original TypeScript, not minified JS.
// Requires SENTRY_AUTH_TOKEN, SENTRY_ORG, SENTRY_PROJECT env vars at build time.
// Set them in your CI secrets / Render environment — they are NOT needed at runtime.
module.exports = withSentryConfig(nextConfig, {
  org: process.env.SENTRY_ORG || "sellervision",
  project: process.env.SENTRY_PROJECT || "sellervision-frontend",
  // Upload source maps only when auth token is present (skips silently in dev)
  authToken: process.env.SENTRY_AUTH_TOKEN,
  silent: !process.env.CI,          // quiet in local builds, verbose in CI
  widenClientFileUpload: true,       // capture more frames in replays
  hideSourceMaps: true,              // don't ship source maps to the browser
  disableLogger: true,               // remove Sentry logger from bundle
  automaticVercelMonitors: false,
});
