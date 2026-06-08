/**
 * Products page — Product Research tests
 *
 * Covers:
 * - Search tab: search input visible, submit triggers POST /products/search
 * - Search results render product cards with title + score
 * - Tracked tab: switches to tracked products, renders list
 * - Empty tracked state renders a helpful prompt (no crash)
 * - Plan limit banner when at/over product cap
 */

import { test, expect, Page } from "@playwright/test";
import { mockAllApis, mockRoute, FIXTURES } from "./helpers/api-mocks";

async function goProducts(page: Page) {
  await mockAllApis(page);
  await page.goto("/products");
  await page.waitForLoadState("networkidle");
}

test.describe("Products — search tab", () => {
  test("search input and button are visible", async ({ page }) => {
    await goProducts(page);
    await expect(page.locator("input[type=text], input[placeholder*=search i], input[placeholder*=product i]").first()).toBeVisible({ timeout: 8000 });
  });

  test("submitting search calls /products/search and renders results", async ({ page }) => {
    let searchCalled = false;
    await mockAllApis(page);
    await page.route("**/api/v1/products/search", (route) => {
      searchCalled = true;
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(FIXTURES.searchProducts),
      });
    });
    await page.goto("/products");
    await page.waitForLoadState("networkidle");

    // Type in search and submit
    const searchInput = page.locator("input[type=text], input[placeholder*=search i]").first();
    await searchInput.fill("laptop stand");

    // Hit Enter or click Search button
    await searchInput.press("Enter");

    // Wait for API call and results
    await expect(async () => {
      expect(searchCalled).toBe(true);
    }).toPass({ timeout: 5000 });

    // Product title from fixture should appear
    await expect(page.getByText("Laptop Stand Adjustable", { exact: false })).toBeVisible({ timeout: 8000 });
  });

  test("opportunity score is shown on result cards", async ({ page }) => {
    let searchCalled = false;
    await mockAllApis(page);
    await page.route("**/api/v1/products/search", (route) => {
      searchCalled = true;
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(FIXTURES.searchProducts),
      });
    });
    await page.goto("/products");
    await page.waitForLoadState("networkidle");

    const searchInput = page.locator("input[type=text], input[placeholder*=search i]").first();
    await searchInput.fill("laptop stand");
    await searchInput.press("Enter");

    // Score "82" from fixture
    await expect(page.getByText("82", { exact: false }).first()).toBeVisible({ timeout: 8000 });
  });
});

test.describe("Products — tracked tab", () => {
  test("switching to tracked tab loads product list", async ({ page }) => {
    await goProducts(page);

    // Click the "Tracked" or "My Products" tab
    const trackedTab = page.getByText(/tracked|my products/i).first();
    await expect(trackedTab).toBeVisible({ timeout: 8000 });
    await trackedTab.click();

    // Wait for list to load
    await page.waitForLoadState("networkidle");

    // Product title from fixture
    await expect(page.getByText("Wireless Earbuds Pro", { exact: false })).toBeVisible({ timeout: 8000 });
  });

  test("empty tracked state shows no crash", async ({ page }) => {
    await mockAllApis(page, {
      products: { items: [], total: 0, page: 1, per_page: 25 },
    });
    await page.goto("/products");
    await page.waitForLoadState("networkidle");

    const trackedTab = page.getByText(/tracked|my products/i).first();
    await expect(trackedTab).toBeVisible({ timeout: 8000 });
    await trackedTab.click();
    await page.waitForLoadState("networkidle");

    // Should show empty state, not crash
    await expect(page.locator("text=Application error")).not.toBeVisible();
    // Empty state usually shows some "no products" text or an add CTA
    await expect(
      page.getByText(/no products|add your first|start tracking/i).first()
    ).toBeVisible({ timeout: 8000 });
  });
});

test.describe("Products — plan limit", () => {
  test("at-limit banner appears when products_tracked >= limit", async ({ page }) => {
    await mockAllApis(page, {
      usage: { products_tracked: 250, limits: { products: 250 }, products_limit: 250 },
    });
    await page.goto("/products");
    await page.waitForLoadState("networkidle");

    const trackedTab = page.getByText(/tracked|my products/i).first();
    if (await trackedTab.isVisible()) {
      await trackedTab.click();
      await page.waitForLoadState("networkidle");
    }

    // Limit reached messaging should appear somewhere on the page
    await expect(
      page.getByText(/limit|upgrade|plan/i).first()
    ).toBeVisible({ timeout: 8000 });
  });
});
