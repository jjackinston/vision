/**
 * Admin panel tests
 *
 * Covers:
 * - Login gate renders (key input + unlock button)
 * - Wrong key → error message appears, no data shown
 * - Correct key → stats tab loads with KPI cards
 * - Tenants tab shows tenant table
 * - Users tab shows user table
 * - Audit logs tab renders (empty state OK)
 * - Tenant edit modal opens and closes
 * - Sign out clears session and returns to login gate
 */

import { test, expect, Page } from "@playwright/test";
import { FIXTURES } from "./helpers/api-mocks";

const ADMIN_KEY = "test-admin-key-abc123";
const API_BASE = "**/api/v1/admin";

/** Mock all admin routes with the given key guard. */
async function mockAdminRoutes(page: Page) {
  await page.route(`${API_BASE}/stats`, (route) => {
    const key = route.request().headers()["x-admin-key"];
    if (key === ADMIN_KEY) {
      route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(FIXTURES.adminStats) });
    } else {
      route.fulfill({ status: 403, contentType: "application/json", body: JSON.stringify({ detail: "Invalid admin key" }) });
    }
  });

  await page.route(`${API_BASE}/tenants**`, (route) => {
    const key = route.request().headers()["x-admin-key"];
    const method = route.request().method();
    if (key === ADMIN_KEY) {
      if (method === "PATCH") {
        route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ updated: true, fields: ["is_active"] }) });
      } else {
        route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(FIXTURES.adminTenants) });
      }
    } else {
      route.fulfill({ status: 403, contentType: "application/json", body: JSON.stringify({ detail: "Invalid admin key" }) });
    }
  });

  await page.route(`${API_BASE}/users**`, (route) => {
    const key = route.request().headers()["x-admin-key"];
    if (key === ADMIN_KEY) {
      route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(FIXTURES.adminUsers) });
    } else {
      route.fulfill({ status: 403, contentType: "application/json", body: JSON.stringify({ detail: "Invalid admin key" }) });
    }
  });

  await page.route(`${API_BASE}/audit-logs**`, (route) => {
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ items: [], total: 0, page: 1, per_page: 50 }),
    });
  });
}

async function unlockAdmin(page: Page) {
  await mockAdminRoutes(page);
  await page.goto("/admin");
  await expect(page.locator("input[type=password]")).toBeVisible({ timeout: 8000 });
  await page.locator("input[type=password]").fill(ADMIN_KEY);
  await page.getByRole("button", { name: /unlock/i }).click();
  // Wait for stats to load (proves the correct key was accepted)
  await expect(page.getByText(/Total Tenants/i)).toBeVisible({ timeout: 8000 });
}

test.describe("Admin — login gate", () => {
  test("shows key input and unlock button", async ({ page }) => {
    await page.goto("/admin");
    await expect(page.getByText("Admin Panel")).toBeVisible({ timeout: 8000 });
    await expect(page.locator("input[type=password]")).toBeVisible();
    await expect(page.getByRole("button", { name: /unlock/i })).toBeVisible();
  });

  test("unlock button is disabled when input is empty", async ({ page }) => {
    await page.goto("/admin");
    const btn = page.getByRole("button", { name: /unlock/i });
    await expect(btn).toBeVisible({ timeout: 5000 });
    await expect(btn).toBeDisabled();
  });

  test("wrong key shows error message", async ({ page }) => {
    await mockAdminRoutes(page);
    await page.goto("/admin");
    await page.locator("input[type=password]").fill("wrong-key");
    await page.getByRole("button", { name: /unlock/i }).click();
    await expect(page.getByText(/invalid admin key/i)).toBeVisible({ timeout: 8000 });
  });

  test("correct key unlocks the dashboard", async ({ page }) => {
    await unlockAdmin(page);
    // Stats overview cards should now be visible
    await expect(page.getByText(/Total Tenants|Paying/i).first()).toBeVisible({ timeout: 8000 });
  });
});

test.describe("Admin — overview tab", () => {
  test("shows KPI stat cards", async ({ page }) => {
    await unlockAdmin(page);
    // From fixture: tenants.total=3, paying=1
    await expect(page.getByText("3")).toBeVisible({ timeout: 8000 });
    await expect(page.getByText("1")).toBeVisible({ timeout: 8000 });
  });

  test("plan distribution is rendered", async ({ page }) => {
    await unlockAdmin(page);
    await expect(page.getByText("Professional", { exact: false }).first()).toBeVisible({ timeout: 8000 });
  });
});

test.describe("Admin — tenants tab", () => {
  test("switching to tenants tab shows tenant table", async ({ page }) => {
    await unlockAdmin(page);
    await page.getByRole("button", { name: /tenants/i }).click();
    await page.waitForLoadState("networkidle");

    // Tenant name from fixture
    await expect(page.getByText("Dev Seller Co", { exact: false })).toBeVisible({ timeout: 8000 });
  });

  test("tenant table shows plan badge", async ({ page }) => {
    await unlockAdmin(page);
    await page.getByRole("button", { name: /tenants/i }).click();
    await page.waitForLoadState("networkidle");

    await expect(page.getByText("Professional", { exact: false }).first()).toBeVisible({ timeout: 8000 });
  });

  test("edit button opens tenant edit modal", async ({ page }) => {
    await unlockAdmin(page);
    await page.getByRole("button", { name: /tenants/i }).click();
    await page.waitForLoadState("networkidle");

    // Click the pencil/edit icon for the first tenant
    const editBtn = page.locator("button svg.lucide-pencil").first();
    // Fallback: any button in the actions column
    const actionBtn = page.locator("table tbody tr:first-child button").last();
    const btn = (await editBtn.count()) > 0 ? editBtn : actionBtn;
    await expect(btn).toBeVisible({ timeout: 5000 });
    await btn.click();

    // Modal should appear
    await expect(page.getByText("Edit Tenant", { exact: false })).toBeVisible({ timeout: 5000 });
  });

  test("edit modal can be closed with Cancel", async ({ page }) => {
    await unlockAdmin(page);
    await page.getByRole("button", { name: /tenants/i }).click();
    await page.waitForLoadState("networkidle");

    const actionBtn = page.locator("table tbody tr:first-child button").last();
    await expect(actionBtn).toBeVisible({ timeout: 5000 });
    await actionBtn.click();

    // Modal open — now close it
    await expect(page.getByText("Edit Tenant")).toBeVisible({ timeout: 5000 });
    await page.getByRole("button", { name: /cancel/i }).click();
    await expect(page.getByText("Edit Tenant")).not.toBeVisible({ timeout: 3000 });
  });
});

test.describe("Admin — users tab", () => {
  test("users tab shows user table", async ({ page }) => {
    await unlockAdmin(page);
    await page.getByRole("button", { name: /users/i }).click();
    await page.waitForLoadState("networkidle");

    await expect(page.getByText("dev@sellervision.local", { exact: false })).toBeVisible({ timeout: 8000 });
  });
});

test.describe("Admin — audit logs tab", () => {
  test("audit logs tab renders without crash", async ({ page }) => {
    await unlockAdmin(page);
    await page.getByRole("button", { name: /audit/i }).click();
    await page.waitForLoadState("networkidle");

    // Empty state (fixture returns []) — should show "No audit logs" not a crash
    await expect(page.locator("text=Application error")).not.toBeVisible();
    await expect(
      page.getByText(/no audit logs|no entries/i).first()
    ).toBeVisible({ timeout: 8000 });
  });
});

test.describe("Admin — sign out", () => {
  test("sign out returns to login gate", async ({ page }) => {
    await unlockAdmin(page);

    // Click sign out button
    const signOutBtn = page.getByRole("button", { name: /sign out|logout/i });
    await expect(signOutBtn).toBeVisible({ timeout: 5000 });
    await signOutBtn.click();

    // Should return to login gate
    await expect(page.locator("input[type=password]")).toBeVisible({ timeout: 5000 });
  });
});
