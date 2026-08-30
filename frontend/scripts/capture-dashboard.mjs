import { chromium } from "@playwright/test";

const baseURL = process.env.PLAYWRIGHT_BASE_URL ?? "http://localhost:5173";
const timestamp = Date.now();
const email = `visual-${timestamp}@example.com`;
const password = "visual-capture-password";

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });

try {
  await page.goto(`${baseURL}/register`);
  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Password").fill(password);
  await page.getByLabel("Time zone").selectOption("America/Los_Angeles");
  await page.getByRole("button", { name: "Create account" }).click();
  await page.waitForURL(/\/goal$/);

  await page.getByLabel("Goal name").fill("Visual capture goal");
  await page.getByLabel("Target amount").fill("4000");
  await page.getByLabel("Initial saved").fill("0");
  await page.getByLabel("Current saved").fill("400");
  await page.getByLabel("Start date").fill("2026-08-01");
  await page.getByLabel("Target date").fill("2026-09-27");
  await page.getByRole("button", { name: "Create goal" }).click();
  await page.getByRole("status").waitFor();

  await page.getByRole("link", { name: /Cash:/ }).click();
  await page.waitForURL(/\/financial-inputs#cash-picture$/);
  const cashForm = page.locator("form#cash-picture");
  await cashForm.getByLabel("Starting cash").fill("1200");
  await cashForm.getByLabel("Balance as of").fill("2026-08-27");
  await cashForm.getByLabel("Reserve buffer").fill("100");
  await cashForm.getByLabel("Protect this reserve").check();
  await cashForm.getByRole("button", { name: "Save cash picture" }).click();
  await page.getByRole("status").waitFor();

  await page.screenshot({ path: "/tmp/goal-wise-financial-inputs-desktop.png", fullPage: true });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.screenshot({ path: "/tmp/goal-wise-financial-inputs-mobile.png", fullPage: true });
  await page.setViewportSize({ width: 1440, height: 1000 });

  const incomeForm = page.locator("form#income-sources");
  await incomeForm.getByLabel("Name").fill("Salary");
  await incomeForm.getByLabel("Amount").fill("2400");
  await incomeForm.getByLabel("Next date").fill("2026-09-01");
  await incomeForm.getByRole("button", { name: "Add income" }).click();
  await page.getByRole("status").waitFor();

  const expenseForm = page.locator("form#planned-expenses");
  await expenseForm.getByLabel("Name").fill("Rent");
  await expenseForm.getByLabel("Amount").fill("900");
  await expenseForm.getByLabel("Next date").fill("2026-09-01");
  await expenseForm.getByRole("button", { name: "Add expense" }).click();
  await page.getByRole("status").waitFor();
  await page.screenshot({ path: "/tmp/goal-wise-financial-inputs-populated-desktop.png", fullPage: true });

  await page.getByRole("link", { name: "View dashboard" }).click();
  await page.waitForURL(/\/dashboard$/);
  await page.getByRole("heading", { name: "Weekly safe-to-spend" }).waitFor();
  await page.screenshot({ path: "/tmp/goal-wise-dashboard-desktop.png", fullPage: true });

  await page.getByRole("link", { name: "View plan details" }).click();
  await page.waitForURL(/\/calculation$/);
  await page.getByRole("heading", { name: "Plan details" }).waitFor();
  await page.screenshot({ path: "/tmp/goal-wise-plan-details-desktop.png", fullPage: true });

  await page.setViewportSize({ width: 390, height: 844 });
  await page.screenshot({ path: "/tmp/goal-wise-plan-details-mobile.png", fullPage: true });

  await page.getByRole("link", { name: "Back to dashboard" }).click();
  await page.waitForURL(/\/dashboard$/);
  await page.getByRole("heading", { name: "Weekly safe-to-spend" }).waitFor();
  await page.screenshot({ path: "/tmp/goal-wise-dashboard-mobile.png", fullPage: true });
} finally {
  await browser.close();
}

console.log("Wrote /tmp/goal-wise-dashboard-desktop.png");
console.log("Wrote /tmp/goal-wise-dashboard-mobile.png");
console.log("Wrote /tmp/goal-wise-financial-inputs-desktop.png");
console.log("Wrote /tmp/goal-wise-financial-inputs-mobile.png");
console.log("Wrote /tmp/goal-wise-financial-inputs-populated-desktop.png");
console.log("Wrote /tmp/goal-wise-plan-details-desktop.png");
console.log("Wrote /tmp/goal-wise-plan-details-mobile.png");
