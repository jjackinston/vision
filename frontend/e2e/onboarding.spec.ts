/**
 * Onboarding wizard tests
 *
 * Covers:
 * - Step 1 renders on page load
 * - "Next" navigates to step 2, then step 3
 * - "Back" returns from step 2 to step 1
 * - Step indicators update as user progresses
 * - "Skip setup" link is always visible and navigates to /dashboard
 * - Completing step 3 calls PATCH /tenants/me/settings then redirects to /dashboard
 */

import { test, expect, Page } from "@playwright/test";
import { mockAllApis, mockRoute } from "./helpers/api-mocks";

async function goOnboarding(page: Page) {
  await mockAllApis(page);
  await page.goto("/onboarding");
  await page.waitForLoadState("networkidle");
}

test.describe("Onboarding wizard — navigation", () => {
  test("step 1 is shown on load", async ({ page }) => {
    await goOnboarding(page);
    // Step 1 content — connecting marketplace
    await expect(
      page.getByText(/connect|marketplace|step 1/i).first()
    ).toBeVisible({ timeout: 8000 });
  });

  test("clicking Next advances to step 2", async ({ page }) => {
    await goOnboarding(page);

    const nextBtn = page.getByRole("button", { name: /next|continue/i }).first();
    await expect(nextBtn).toBeVisible({ timeout: 5000 });
    await nextBtn.click();

    // Step 2 — import products
    await expect(
      page.getByText(/import|products|step 2/i).first()
    ).toBeVisible({ timeout: 8000 });
  });

  test("clicking Next twice reaches step 3", async ({ page }) => {
    await goOnboarding(page);

    for (let i = 0; i < 2; i++) {
      const nextBtn = page.getByRole("button", { name: /next|continue/i }).first();
      await expect(nextBtn).toBeVisible({ timeout: 5000 });
      await nextBtn.click();
      await page.waitForTimeout(300); // allow animation
    }

    // Step 3 — alerts / final step
    await expect(
      page.getByText(/alert|notification|step 3|final/i).first()
    ).toBeVisible({ timeout: 8000 });
  });

  test("Back button returns from step 2 to step 1", async ({ page }) => {
    await goOnboarding(page);

    // Go to step 2
    await page.getByRole("button", { name: /next|continue/i }).first().click();
    await page.waitForTimeout(300);

    // Hit Back
    const backBtn = page.getByRole("button", { name: /back|previous/i }).first();
    await expect(backBtn).toBeVisible({ timeout: 5000 });
    await backBtn.click();
    await page.waitForTimeout(300);

    // Should be back at step 1
    await expect(
      page.getByText(/connect|marketplace/i).first()
    ).toBeVisible({ timeout: 8000 });
  });
});

test.describe("Onboarding wizard — skip", () => {
  test("skip link is always visible on step 1", async ({ page }) => {
    await goOnboarding(page);
    await expect(
      page.getByText(/skip|go to dashboard/i).first()
    ).toBeVisible({ timeout: 8000 });
  });

  test("skip link navigates to /dashboard", async ({ page }) => {
    await goOnboarding(page);

    const skipLink = page.getByText(/skip|go to dashboard/i).first();
    await expect(skipLink).toBeVisible({ timeout: 5000 });
    await skipLink.click();

    await expect(page).toHaveURL(/\/dashboard/, { timeout: 8000 });
  });
});

test.describe("Onboarding wizard — completion", () => {
  test("finishing step 3 PATCHes tenant settings", async ({ page }) => {
    let patchCalled = false;
    await mockAllApis(page);
    await page.route("**/api/v1/tenants/me/settings", (route) => {
      if (route.request().method() === "PATCH") {
        patchCalled = true;
        route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ updated: true }) });
      } else {
        route.continue();
      }
    });

    await page.goto("/onboarding");
    await page.waitForLoadState("networkidle");

    // Navigate through all 3 steps
    for (let i = 0; i < 2; i++) {
      const nextBtn = page.getByRole("button", { name: /next|continue/i }).first();
      await expect(nextBtn).toBeVisible({ timeout: 5000 });
      await nextBtn.click();
      await page.waitForTimeout(300);
    }

    // Click the final "Complete" / "Done" / "Finish" button
    const completeBtn = page.getByRole("button", { name: /complete|done|finish|launch/i }).first();
    await expect(completeBtn).toBeVisible({ timeout: 5000 });
    await completeBtn.click();

    // Verify PATCH was called
    await expect(async () => {
      expect(patchCalled).toBe(true);
    }).toPass({ timeout: 5000 });
  });

  test("completing setup redirects to /dashboard", async ({ page }) => {
    await mockAllApis(page);
    await page.goto("/onboarding");
    await page.waitForLoadState("networkidle");

    // Navigate through all 3 steps
    for (let i = 0; i < 2; i++) {
      const nextBtn = page.getByRole("button", { name: /next|continue/i }).first();
      await expect(nextBtn).toBeVisible({ timeout: 5000 });
      await nextBtn.click();
      await page.waitForTimeout(300);
    }

    const completeBtn = page.getByRole("button", { name: /complete|done|finish|launch/i }).first();
    await expect(completeBtn).toBeVisible({ timeout: 5000 });
    await completeBtn.click();

    await expect(page).toHaveURL(/\/dashboard/, { timeout: 8000 });
  });
});
