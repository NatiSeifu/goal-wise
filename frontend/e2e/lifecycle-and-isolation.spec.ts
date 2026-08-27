import { expect, test } from "@playwright/test";

import {
  createGoal,
  dateFromToday,
  registerUser,
  type DashboardScenario,
} from "./support/flows.ts";

const lifecycleGoal: DashboardScenario = {
  currentSaved: 500,
  name: "Trip fund",
  startingCash: 1000,
  target: 3000,
};

test("archives an active goal and allows a replacement goal", async ({ page }) => {
  await registerUser(page);
  await createGoal(page, lifecycleGoal);

  await expect(page.getByText("Trip fund")).toBeVisible();
  await page.getByRole("button", { name: "Archive active goal" }).click();
  await expect(page.getByRole("status")).toContainText("Goal archived.");
  await expect(page.getByText("Trip fund")).not.toBeVisible();

  await page.getByLabel("Goal name").fill("Replacement fund");
  await page.getByLabel("Target amount").fill("2000");
  await page.getByLabel("Initial saved").fill("0");
  await page.getByLabel("Current saved").fill("0");
  await page.getByLabel("Start date").fill(dateFromToday(-1));
  await page.getByLabel("Target date").fill(dateFromToday(90));
  await page.getByRole("button", { name: "Create goal" }).click();

  await expect(page.getByRole("status")).toContainText("Goal saved.");
  await expect(page.getByText("Replacement fund")).toBeVisible();
});

test("rejects another user's attempt to archive the goal", async ({ browser }) => {
  const ownerContext = await browser.newContext();
  const ownerPage = await ownerContext.newPage();
  const otherContext = await browser.newContext();
  const otherPage = await otherContext.newPage();

  try {
    await registerUser(ownerPage);

    const goalResponsePromise = ownerPage.waitForResponse(
      (response) => response.url().endsWith("/api/v1/goals") && response.request().method() === "POST",
    );
    await createGoal(ownerPage, { ...lifecycleGoal, name: "Private goal" });
    const goalResponse = await goalResponsePromise;
    const goalId = (await goalResponse.json()).item.id as string;

    await registerUser(otherPage);
    const currentUserResponse = await otherPage.request.get("http://localhost:8000/api/v1/auth/me");
    const { item } = await currentUserResponse.json();

    const archiveResponse = await otherPage.request.post(`http://localhost:8000/api/v1/goals/${goalId}/archive`, {
      headers: { "X-CSRF-Token": item.csrf_token },
    });

    expect(archiveResponse.status()).toBe(404);
  } finally {
    await ownerContext.close();
    await otherContext.close();
  }
});
