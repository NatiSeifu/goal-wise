import { expect, test, type Page } from "@playwright/test";

import {
  completeGoalAndCashSetup,
  registerUser,
} from "./support/flows.ts";

const readyScenario = {
  currentSaved: 3_333,
  name: "AI test goal",
  startingCash: 10_000,
  target: 10_000,
};

function mockAiAvailability(page: Page) {
  return page.route("**/api/v1/ai-explanations/status", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({ enabled: true }),
    });
  });
}

test("generates and displays an AI plan insight", async ({ page }) => {
  await mockAiAvailability(page);
  await page.route("**/api/v1/ai-explanations/latest", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({
        enabled: true,
        item: {
          snapshot_id: "e2e-snapshot",
          calculated_at: "2026-08-29T11:27:00Z",
          formula_version: "pace-v1",
          source: "generated",
          explanation: {
            schema_version: "ai-explanation-v1",
            headline: "Your goal may need a little adjustment",
            body: "You still have room to spend each week while keeping your goal in view.",
            observations: [],
            next_step: "Review your goal timeline and keep your plan up to date.",
          },
        },
      }),
    });
  });

  await registerUser(page);
  await completeGoalAndCashSetup(page, readyScenario);

  await expect(page.getByRole("heading", { name: "Plan insights" })).toBeVisible();
  await page.getByRole("button", { name: "Generate analysis" }).click();

  await expect(page.getByRole("heading", { name: "Your goal may need a little adjustment" })).toBeVisible();
  await expect(page.getByText("You still have room to spend each week while keeping your goal in view.")).toBeVisible();
  await expect(page.getByText("Review your goal timeline and keep your plan up to date.")).toBeVisible();
});

test("shows a retryable state when AI analysis is unavailable", async ({ page }) => {
  await mockAiAvailability(page);
  await page.route("**/api/v1/ai-explanations/latest", async (route) => {
    await route.fulfill({
      status: 503,
      contentType: "application/json",
      body: JSON.stringify({
        error: {
          code: "ai_explanation_unavailable",
          message: "We could not prepare an explanation right now. Please try again later.",
        },
      }),
    });
  });

  await registerUser(page);
  await completeGoalAndCashSetup(page, readyScenario);

  await page.getByRole("button", { name: "Generate analysis" }).click();

  await expect(page.getByRole("heading", { name: "Explanation unavailable" })).toBeVisible();
  await expect(page.getByText("We could not prepare an explanation right now. Please try again later.")).toBeVisible();
  await expect(page.getByRole("button", { name: "Try again" })).toBeVisible();
});
