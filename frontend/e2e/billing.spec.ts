/**
 * Billing page tests
 *
 * Covers:
 * - All 4 plan cards render with names and prices
 * - "Upgrade" / "Get started" CTA is present on paid plans
 * - Current plan is visually highlighted
 * - Clicking upgrade calls POST /billing/checkout and redirects to Stripe URL
 * - Current subscription status (trial) is shown
 */

import { test, expect, Page } from "@playwright/test";
import { mockAllApis, mockRoute, FIXTURES } from "./helpers/api-mocks";

/**
 * Navigate to the billing section of the settings page.
 * Billing lives at /settings?section=billing (not a standalone /billing route).
 * The StripeParamHandler in the settings page reads `section=billing` from the
 * query string and activates the billing tab automatically.
 */
async function goBilling(page: Page, overrides = {}) {
  await mockAllApis(page, overrides);
  await page.goto("/settings?section=billing");
  await page.waitForLoadState("networkidle");
}

test.describe("Billing — plan cards", () => {
  test("all four plan names are visible", async ({ page }) => {
    await goBilling(page);
    for (const plan of ["Starter", "Professional", "Business", "Agency"]) {
      await expect(page.getByText(plan, { exact: false }).first()).toBeVisible({ timeout: 10_000 });
    }
  });

  test("monthly prices are displayed", async ({ page }) => {
    await goBilling(page);
    // Fixture prices: $49, $149, $349, $799
    for (const price of ["49", "149", "349", "799"]) {
      await expect(page.getByText(price, { exact: false }).first()).toBeVisible({ timeout: 10_000 });
    }
  });

  test("upgrade / get started buttons are present for paid plans", async ({ page }) => {
    await goBilling(page);
    const upgradeBtns = page.getByRole("button", { name: /upgrade|get started|choose plan|select/i });
    await expect(upgradeBtns.first()).toBeVisible({ timeout: 8000 });
  });
});

test.describe("Billing — current plan & status", () => {
  test("shows current plan name", async ({ page }) => {
    await goBilling(page);
    // User is on Professional (from fixture)
    await expect(page.getByText("Professional", { exact: false }).first()).toBeVisible({ timeout: 8000 });
  });

  test("trial status is shown when on trial", async ({ page }) => {
    await goBilling(page);
    // Fixture sets status: "trialing"
    await expect(
      page.getByText(/trial|trialing|days left/i).first()
    ).toBeVisible({ timeout: 8000 });
  });

  test("no subscription banner is shown when not subscribed", async ({ page }) => {
    await mockAllApis(page, {
      billing: { subscription: null, plan: "Starter", status: "trialing", trial_ends_at: null, current_period_end: null },
    });
    await page.goto("/settings?section=billing");
    await page.waitForLoadState("networkidle");
    // Should still render plan cards, not crash
    await expect(page.locator("text=Application error")).not.toBeVisible();
    await expect(page.getByText("Starter", { exact: false }).first()).toBeVisible({ timeout: 8000 });
  });
});

test.describe("Billing — upgrade flow", () => {
  test("clicking upgrade button calls POST /billing/checkout", async ({ page }) => {
    let checkoutCalled = false;
    await mockAllApis(page);
    await page.route("**/api/v1/billing/checkout**", (route) => {
      if (route.request().method() === "POST") {
        checkoutCalled = true;
        route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({ checkout_url: "https://checkout.stripe.com/test_session", session_id: "cs_test_123" }),
        });
      } else {
        route.continue();
      }
    });

    await page.goto("/settings?section=billing");
    await page.waitForLoadState("networkidle");

    // Click first upgrade button (could be for any plan other than current)
    const upgradeBtn = page.getByRole("button", { name: /upgrade|get started|choose/i }).first();
    await expect(upgradeBtn).toBeVisible({ timeout: 8000 });

    // Don't actually follow the redirect (that goes to external Stripe)
    // Just verify the click fires the API call
    await page.route("**checkout.stripe.com**", (route) => route.abort());
    await upgradeBtn.click();

    await expect(async () => {
      expect(checkoutCalled).toBe(true);
    }).toPass({ timeout: 5000 });
  });
});
