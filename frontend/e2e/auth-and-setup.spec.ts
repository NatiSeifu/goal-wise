import { expect, test } from "@playwright/test";

function uniqueEmail() {
  return `playwright-${Date.now()}@example.com`;
}

const password = "playwright-password";

function dateFromToday(daysFromToday: number) {
  const date = new Date();
  date.setDate(date.getDate() + daysFromToday);
  return [date.getFullYear(), date.getMonth() + 1, date.getDate()]
    .map((part) => String(part).padStart(2, "0"))
    .join("-");
}

test("registers a user and reaches the authenticated dashboard setup state", async ({ page }) => {
  await page.goto("/register");

  await page.getByLabel("Email").fill(uniqueEmail());
  await page.getByLabel("Password").fill(password);
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

test("logs out and signs back in to a protected account", async ({ page }) => {
  const email = uniqueEmail();

  await page.goto("/register");
  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Password").fill(password);
  await page.getByLabel("Time zone").fill("America/Los_Angeles");
  await page.getByRole("button", { name: "Create account" }).click();

  await expect(page).toHaveURL(/\/goal$/);
  await page.getByRole("button", { name: "Sign out" }).click();

  await expect(page).toHaveURL(/\/login$/);
  await page.goto("/dashboard");
  await expect(page).toHaveURL(/\/login$/);

  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Password").fill(password);
  await page.getByRole("button", { name: "Sign in" }).click();

  await expect(page).toHaveURL(/\/dashboard$/);
  await expect(page.getByRole("heading", { name: "Dashboard" })).toBeVisible();
});

test("completes the first-run setup and reaches a ready dashboard", async ({ page }) => {
  await page.goto("/register");
  await page.getByLabel("Email").fill(uniqueEmail());
  await page.getByLabel("Password").fill(password);
  await page.getByLabel("Time zone").fill("America/Los_Angeles");
  await page.getByRole("button", { name: "Create account" }).click();

  await expect(page).toHaveURL(/\/goal$/);
  await page.getByLabel("Goal name").fill("Emergency fund");
  await page.getByLabel("Target amount").fill("3000");
  await page.getByLabel("Initial saved").fill("500");
  await page.getByLabel("Current saved").fill("500");
  await page.getByLabel("Start date").fill(dateFromToday(-7));
  await page.getByLabel("Target date").fill(dateFromToday(45));
  await page.getByRole("button", { name: "Create goal" }).click();
  await expect(page.getByRole("status")).toContainText("Goal saved");

  await page.getByRole("link", { name: /Cash:/ }).click();
  await expect(page).toHaveURL(/\/financial-inputs#cash-picture$/);
  const cashForm = page.locator("form#cash-picture");
  await cashForm.getByLabel("Starting cash").fill("1200");
  await cashForm.getByLabel("Balance as of").fill(dateFromToday(0));
  await cashForm.getByLabel("Reserve buffer").fill("100");
  await cashForm.getByLabel("Protect this reserve").check();
  await cashForm.getByRole("button", { name: "Save cash picture" }).click();
  await expect(page.getByRole("status")).toContainText("Cash picture saved.");

  const incomeForm = page.locator("form#income-sources");
  await incomeForm.getByLabel("Name").fill("Monthly salary");
  await incomeForm.getByLabel("Amount").fill("1500");
  await incomeForm.getByLabel("Next date").fill(dateFromToday(1));
  await incomeForm.getByLabel("Frequency").selectOption("monthly");
  await incomeForm.getByLabel("Confidence").selectOption("confirmed");
  await incomeForm.getByRole("button", { name: "Add income" }).click();
  await expect(page.getByRole("status")).toContainText("Income source saved.");

  const expenseForm = page.locator("form#planned-expenses");
  await expenseForm.getByLabel("Name").fill("Rent");
  await expenseForm.getByLabel("Amount").fill("800");
  await expenseForm.getByLabel("Next date").fill(dateFromToday(7));
  await expenseForm.getByLabel("Frequency").selectOption("monthly");
  await expenseForm.getByLabel("Classification").selectOption("essential");
  await expenseForm.getByRole("button", { name: "Add expense" }).click();
  await expect(page.getByRole("status")).toContainText("Planned expense saved.");

  await page.getByRole("link", { name: "View dashboard" }).click();
  await expect(page).toHaveURL(/\/dashboard$/);
  await expect(page.getByRole("heading", { name: "Weekly safe-to-spend" })).toBeVisible();
  await expect(page.getByText("Emergency fund")).toBeVisible();
  await expect(page.getByText(/^(Completed|Off Pace|Ahead|At Risk|On Track)$/)).toBeVisible();
});
