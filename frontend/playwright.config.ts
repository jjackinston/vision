import { defineConfig, devices } from "@playwright/test";

/**
 * SellerVision AI — Playwright E2E config
 *
 * Tests intercept all /api/v1/* calls via page.route(), so they run
 * deterministically against the Next.js dev server with no real backend.
 *
 * Run all tests:      npm run test:e2e
 * Interactive UI:     npm run test:e2e:ui
 * Debug single test:  npm run test:e2e:debug
 */
export default defineConfig({
  testDir: "./e2e",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 2 : undefined,
  timeout: 30_000,
  reporter: [
    ["html", { outputFolder: "playwright-report", open: "never" }],
    ["list"],
  ],

  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL ?? "http://localhost:3001",
    trace: "on-first-retry",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
    // Don't set a real Clerk key — middleware will pass-through all requests
    extraHTTPHeaders: {},
  },

  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
    // Uncomment to run in more browsers:
    // { name: "firefox", use: { ...devices["Desktop Firefox"] } },
    // { name: "webkit",  use: { ...devices["Desktop Safari"]  } },
  ],

  // Start the Next.js dev server automatically when running tests
  webServer: {
    command: "npm run dev -- --port 3001",
    url: "http://localhost:3001",
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
    env: {
      // Ensure Clerk bypass is active (no publishable key → middleware passes through)
      NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY: "",
    },
  },
});
