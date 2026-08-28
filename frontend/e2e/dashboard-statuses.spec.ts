import { expect, test } from "@playwright/test";

import {
  completeGoalAndCashSetup,
  registerUser,
  type DashboardScenario,
} from "./support/flows.ts";

const scenarios: Array<DashboardScenario & { expectedStatus: string }> = [
  { currentSaved: 1_000, expectedStatus: "Off Pace", name: "Off pace goal", startingCash: 100, target: 10_000 },
  { currentSaved: 5_000, expectedStatus: "Ahead", name: "Ahead goal", startingCash: 5_000, target: 10_000 },
  { currentSaved: 0, expectedStatus: "At Risk", name: "At risk goal", startingCash: 10_000, target: 10_000 },
  { currentSaved: 3_333, expectedStatus: "On Track", name: "On track goal", startingCash: 10_000, target: 10_000 },
];

for (const scenario of scenarios) {
  test(`renders the ${scenario.expectedStatus} dashboard state`, async ({ page }) => {
    await registerUser(page);
    await completeGoalAndCashSetup(page, scenario);

    await expect(page.getByRole("heading", { name: "Weekly safe-to-spend" })).toBeVisible();
    await expect(page.getByText(scenario.name)).toBeVisible();
    await expect(page.getByText(scenario.expectedStatus, { exact: true })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Risk view" })).toBeVisible();
  });
}
