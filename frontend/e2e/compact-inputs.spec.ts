import { expect, test } from "@playwright/test";
import { completeGoalAndCashSetup, dateFromToday, registerUser } from "./support/flows.ts";

test("adds, edits, and removes income through the compact mobile controls", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await registerUser(page);
  await completeGoalAndCashSetup(page, { name: "Moving fund", target: 3000, currentSaved: 1000, startingCash: 2500 });
  await page.getByRole("link", { name: "Inputs", exact: true }).click();

  const form = page.locator("form#income-sources");
  await form.getByLabel("Name").fill("Salary");
  await form.getByLabel("Amount").fill("1500");
  await form.getByLabel("Next date").fill(dateFromToday(7));
  await form.getByRole("button", { name: "Add income" }).click();

  const list = page.getByRole("region", { name: "Income in plan" });
  await expect(list.getByRole("heading", { name: "Salary" })).toBeVisible();
  await expect(form).not.toBeVisible();
  await list.getByRole("button", { name: "Edit", exact: true }).click();
  await expect(form.getByLabel("Name")).toBeFocused();
  await form.getByLabel("Amount").fill("1700");
  await form.getByRole("button", { name: "Save income" }).click();
  await expect(list.getByText("$1,700", { exact: true })).toBeVisible();
  await expect(form).not.toBeVisible();

  const add = page.locator("summary").filter({ hasText: "Add income source" });
  await add.focus();
  await page.keyboard.press("Enter");
  await expect(form.getByRole("button", { name: "Add income" })).toBeVisible();
  await expect(form.getByLabel("Name")).toHaveValue("");
  await list.getByRole("button", { name: "Remove", exact: true }).click();
  await expect(list.getByText("No income added.")).toBeVisible();
  await expect(form).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
});
