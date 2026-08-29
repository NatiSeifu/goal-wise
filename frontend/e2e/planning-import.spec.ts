import { expect, test } from "@playwright/test";
import path from "node:path";

import { registerUser } from "./support/flows.ts";

test("reviews and confirms a complete planning CSV", async ({ page }) => {
  await registerUser(page);
  await page.getByRole("link", { name: "Import plan" }).click();
  await page.waitForURL(/\/planning-import$/);

  await page.getByLabel("GoalWise planning CSV").setInputFiles(
    path.resolve("public/planning-import-template.csv"),
  );
  await page.getByRole("button", { name: "Review file" }).click();

  await expect(page.getByRole("heading", { name: "Ready to import" })).toBeVisible();
  await expect(page.getByText("Moving fund")).toBeVisible();
  await expect(page.getByRole("heading", { name: "Expected income" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Planned expenses" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Confirm import" })).toBeVisible();

  await page.getByRole("button", { name: "Confirm import" }).click();

  await expect(page.getByRole("status")).toContainText("Your plan was imported.");
  await page.getByRole("link", { name: "Dashboard" }).click();
  await page.waitForURL(/\/dashboard$/);
  await expect(page.getByText("Moving fund")).toBeVisible();
});

test("keeps an invalid planning CSV in review with row errors", async ({ page }) => {
  await registerUser(page);
  await page.getByRole("link", { name: "Import plan" }).click();

  await page.getByLabel("GoalWise planning CSV").setInputFiles({
    name: "invalid-plan.csv",
    mimeType: "text/csv",
    buffer: Buffer.from([
      "record_type,name,target_amount,initial_saved,current_saved,starting_cash,balance_date,reserve_buffer,amount,date,frequency,confidence,classification,start_date,target_date",
      "goal,Trip,10.00,0.00,0.00,,,,,,,,,2026-08-28,2026-08-27",
      "cash,,,,,100.00,2026-08-28,5.00,,,,,,,",
    ].join("\n")),
  });
  await page.getByRole("button", { name: "Review file" }).click();

  await expect(page.getByRole("alert")).toContainText("could not be imported");
  await expect(page.getByText(/Row 2, target_date/)).toBeVisible();
  await expect(page.getByRole("button", { name: "Confirm import" })).not.toBeVisible();
});
