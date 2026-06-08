/**
 * Smoke tests — navigate every dashboard route and verify the page
 * renders without a JS crash, an error boundary, or a hard 500.
 *
 * These are the widest-net tests: they catch broken imports, missing
 * component exports, and critical render failures that would surface
 * to every user.
 */

import { test, expect } from "@playwright/test";
import { mockAllApis } from "./helpers/api-mocks";

// All dashboard routes to smoke-test
const DASHBOARD_ROUTES = [
  { path: "/dashboard",    label: "AI CEO Dashboard" },
  { path: "/products",     label: "Product Research" },
  { path: "/keywords",     label: "Keyword" },
  { path: "/analytics",   label: "Analytics" },
  { path: "/inventory",   label: "Inventory" },
  { path: "/competitors",  label: "Competitor" },
  { path: "/trends",       label: "Trend" },
  { path: "/ppc",          label: "PPC" },
  { path: "/automation",   label: "Automation" },
  { path: "/marketplace",  label: "Marketplace" },
  { path: "/suppliers",    label: "Supplier" },
  { path: "/listings",     label: "Listing" },
  { path: "/agents",       label: "Agent" },
  { path: "/settings",     label: "Settings" },
];

// Auth routes
const AUTH_ROUTES = [
  { path: "/login",    label: "Sign in" },
  { path: "/register", label: "Sign up" },
];

test.describe("Smoke — dashboard pages", () => {
  for (const { path, label } of DASHBOARD_ROUTES) {
    test(`${path} renders without crash`, async ({ page }) => {
      await mockAllApis(page);
      await page.goto(path);

      // Page must not show Next.js error boundary
      await expect(page.locator("text=Application error")).not.toBeVisible({ timeout: 8000 });
      await expect(page.locator("text=500")).not.toBeVisible();

      // Page title or heading should contain the expected keyword (case-insensitive)
      const body = page.locator("body");
      await expect(body).toBeVisible();

      // Check for visible text matching the route label — confirms the right page loaded
      await expect(
        page.getByText(label, { exact: false }).first()
      ).toBeVisible({ timeout: 10_000 });
    });
  }
});

test.describe("Smoke — auth pages", () => {
  for (const { path, label } of AUTH_ROUTES) {
    test(`${path} renders`, async ({ page }) => {
      await page.goto(path);
      await expect(page.getByText(label, { exact: false }).first()).toBeVisible({ timeout: 8000 });
      await expect(page.locator("text=Application error")).not.toBeVisible();
    });
  }
});

test.describe("Smoke — misc pages", () => {
  test("/admin renders login gate", async ({ page }) => {
    // Admin is outside the dashboard layout — does NOT need api mocks to render the login gate
    await page.goto("/admin");
    await expect(page.getByText("Admin Panel")).toBeVisible({ timeout: 8000 });
    await expect(page.locator("input[type=password]")).toBeVisible();
  });

  test("/ root page renders", async ({ page }) => {
    await mockAllApis(page);
    await page.goto("/");
    await expect(page.locator("body")).toBeVisible();
  });

  test("/onboarding renders", async ({ page }) => {
    await mockAllApis(page);
    await page.goto("/onboarding");
    await expect(page.getByText(/marketplace|connect|setup/i).first()).toBeVisible({ timeout: 8000 });
  });
});
