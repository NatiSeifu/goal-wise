import type { Page } from "@playwright/test";

export const testPassword = "playwright-password";

export type DashboardScenario = {
  currentSaved: number;
  name: string;
  startingCash: number;
  target: number;
};

export function uniqueEmail() {
  return `playwright-${Date.now()}-${Math.random().toString(16).slice(2)}@example.com`;
}

export function dateFromToday(daysFromToday: number) {
  const date = new Date();
  date.setDate(date.getDate() + daysFromToday);
  return [date.getFullYear(), date.getMonth() + 1, date.getDate()]
    .map((part) => String(part).padStart(2, "0"))
    .join("-");
}

export async function registerUser(page: Page) {
  const email = uniqueEmail();

  await page.goto("/register");
  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Password").fill(testPassword);
  await page.getByLabel("Time zone").selectOption("America/Los_Angeles");
  await page.getByRole("button", { name: "Create account" }).click();
  await page.waitForURL(/\/goal$/);

  return { email, password: testPassword };
}

export async function createGoal(page: Page, scenario: DashboardScenario) {
  await page.getByLabel("Goal name").fill(scenario.name);
  await page.getByLabel("Target amount").fill(String(scenario.target));
  await page.getByLabel("Initial saved").fill("0");
  await page.getByLabel("Current saved").fill(String(scenario.currentSaved));
  await page.getByLabel("Start date").fill(dateFromToday(-30));
  await page.getByLabel("Target date").fill(dateFromToday(60));
  await page.getByRole("button", { name: "Create goal" }).click();
  await page.getByRole("status").waitFor();
}

export async function completeGoalAndCashSetup(page: Page, scenario: DashboardScenario) {
  await createGoal(page, scenario);

  await page.getByRole("link", { name: /Cash:/ }).click();
  await page.waitForURL(/\/financial-inputs#cash-picture$/);
  const cashForm = page.locator("form#cash-picture");
  await cashForm.getByLabel("Starting cash").fill(String(scenario.startingCash));
  // Keep the fixture valid when CI's UTC date has crossed midnight before the user's local date.
  await cashForm.getByLabel("Balance as of").fill(dateFromToday(-1));
  await cashForm.getByLabel("Reserve buffer").fill("0");
  await cashForm.getByLabel("Protect this reserve").check();
  await cashForm.getByRole("button", { name: "Save cash picture" }).click();
  await page.getByRole("status").waitFor();

  await page.getByRole("link", { name: "View dashboard" }).click();
  await page.waitForURL(/\/dashboard$/);
}
