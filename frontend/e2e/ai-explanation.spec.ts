import { expect, test, type Page } from "@playwright/test";
import { completeGoalAndCashSetup, registerUser } from "./support/flows.ts";
import digest from "../scripts/ai-digest-fixture.json" with { type: "json" };

const readyScenario = { currentSaved: 3_333, name: "AI test goal", startingCash: 10_000, target: 10_000 };

async function prepareDashboard(page: Page) {
  await page.route("**/api/v1/ai-explanations/status", (route) => route.fulfill({ json: { enabled: true } }));
  await registerUser(page);
  const ready = page.waitForResponse(async (response) => response.url().endsWith("/api/v1/dashboard") &&
    response.ok() && (await response.json()).item.status === "ready");
  await completeGoalAndCashSetup(page, readyScenario);
  return (await (await ready).json()).item;
}

test("shows a substantial digest near the top only after an explicit request", async ({ page }) => {
  const dashboard = await prepareDashboard(page);
  let calls = 0;
  await page.route("**/api/v1/ai-explanations/latest", async (route) => {
    calls++;
    await route.fulfill({ json: { enabled: true, item: {
      snapshot_id: dashboard.snapshot_id, calculated_at: dashboard.calculated_at,
      formula_version: "pace-v1", source: "generated", explanation: digest,
    } } });
  });
  const panel = page.getByRole("region", { name: "Plan digest" });
  await expect(panel.getByRole("button", { name: "Generate digest" })).toBeVisible();
  expect(calls).toBe(0);
  expect(await panel.evaluate((element) => element.nextElementSibling?.classList.contains("dashboard-goal-story"))).toBe(true);
  await panel.getByRole("button", { name: "Generate digest" }).click();
  await expect(panel.getByRole("heading", { name: digest.headline })).toBeVisible();
  for (const observation of digest.observations) await expect(panel.getByText(observation.text, { exact: true })).toBeVisible();
  await expect(panel.getByRole("heading", { name: "What to do next" })).toBeVisible();
  await expect(panel.getByText(/AI-generated/)).toBeVisible();
  await panel.getByRole("link", { name: "Review inputs" }).click();
  await expect(page).toHaveURL(/\/financial-inputs$/);
  expect(calls).toBe(1);
});

test("keeps the dashboard usable when generation fails and offers retry", async ({ page }) => {
  await prepareDashboard(page);
  await page.route("**/api/v1/ai-explanations/latest", (route) => route.fulfill({
    status: 503, json: { error: { code: "ai_explanation_unavailable", message: "We could not prepare an explanation right now. Please try again later." } },
  }));
  await page.getByRole("button", { name: "Generate digest" }).click();
  await expect(page.getByRole("heading", { name: "Digest unavailable" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Try again" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Weekly safe-to-spend" })).toBeVisible();
});

test("rejects a digest for a different snapshot", async ({ page }) => {
  await prepareDashboard(page);
  await page.route("**/api/v1/ai-explanations/latest", (route) => route.fulfill({ json: {
    enabled: true, item: { snapshot_id: "older-snapshot", calculated_at: "2026-08-29T11:27:00Z", formula_version: "pace-v1", source: "generated", explanation: digest },
  } }));
  await page.getByRole("button", { name: "Generate digest" }).click();
  await expect(page.getByText("Your plan changed. Reload the dashboard to read the latest digest.")).toBeVisible();
  await expect(page.getByRole("heading", { name: digest.headline })).not.toBeVisible();
});

test("renders the full digest and its action on mobile", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  const dashboard = await prepareDashboard(page);
  await page.route("**/api/v1/ai-explanations/latest", (route) => route.fulfill({ json: {
    enabled: true, item: { snapshot_id: dashboard.snapshot_id, calculated_at: dashboard.calculated_at, formula_version: "pace-v1", source: "generated", explanation: { ...digest, next_step_action: "review_goal" } },
  } }));
  await page.getByRole("button", { name: "Generate digest" }).click();
  const panel = page.getByRole("region", { name: "Plan digest" });
  await expect(panel.getByRole("heading", { name: "What to do next" })).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await panel.getByRole("link", { name: "Review goal" }).click();
  await expect(page.getByLabel("Goal name")).toHaveValue(readyScenario.name);
});
