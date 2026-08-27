import { expect, test } from "@playwright/test";

function uniqueEmail() {
  return `playwright-${Date.now()}@example.com`;
}

test("registers a user and reaches the authenticated dashboard setup state", async ({ page }) => {
  await page.goto("/register");

  await page.getByLabel("Email").fill(uniqueEmail());
  await page.getByLabel("Password").fill("playwright-password");
  await page.getByLabel("Time zone").fill("America/Los_Angeles");
  await page.getByRole("button", { name: "Create account" }).click();

  await expect(page).toHaveURL(/\/goal$/);
  await expect(page.getByRole("heading", { name: "Goal setup" })).toBeVisible();
  await expect(page.getByRole("link", { name: /Dashboard:/ })).toBeVisible();

  await page.getByRole("link", { name: /Dashboard:/ }).click();

  await expect(page).toHaveURL(/\/dashboard$/);
  await expect(page.getByRole("heading", { name: "Dashboard" })).toBeVisible();
  await expect(page.getByText("Finish setup to calculate your weekly plan")).toBeVisible();
});
