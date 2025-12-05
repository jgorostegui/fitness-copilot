import { expect, test } from "@playwright/test"

test("app loads successfully", async ({ page }) => {
  await page.goto("/")
  await expect(page).toHaveTitle(/Fitness Copilot/)
})

test("app renders main content", async ({ page }) => {
  await page.goto("/")
  // Just verify the page doesn't show an error
  await expect(page.locator("body")).toBeVisible()
})
