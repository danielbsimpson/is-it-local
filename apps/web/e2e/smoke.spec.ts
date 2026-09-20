import { expect, test } from "@playwright/test";

/**
 * Deferred smoke test: exercises the primary search-to-detail flow.
 * Requires the API and web dev server running. Not executed in CI yet.
 */
test("home page renders the search form", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Is it local?" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Search" })).toBeVisible();
});

test("searching by name shows results", async ({ page }) => {
  await page.goto("/");
  await page.getByPlaceholder("e.g. Corner Bakery").fill("Bakery");
  await page.getByRole("button", { name: "Search" }).click();
  await expect(page).toHaveURL(/\/search\?/);
  await expect(page.getByRole("heading", { name: "Results" })).toBeVisible();
});
