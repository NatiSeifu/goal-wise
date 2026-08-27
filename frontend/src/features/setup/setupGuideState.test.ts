import { describe, expect, it } from "vitest";

import type {
  DashboardItem,
  FinancialProfileResponse,
  IncomeSourceResponse,
  PlannedExpenseResponse,
} from "../../api/types.ts";
import { setupGuideStateFromDashboard, setupGuideStateFromInputs } from "./setupGuideState.ts";

describe("setup guide state", () => {
  it("keeps completion consistent across form routes", () => {
    const state = setupGuideStateFromInputs({
      currentStep: "goal",
      expenses: [plannedExpense()],
      hasGoal: true,
      incomeSources: [incomeSource()],
      profile: financialProfile({ reserve_buffer_confirmed: true }),
    });

    expect(state).toEqual({
      activeStep: "goal",
      completedSteps: ["goal", "profile", "income", "expenses"],
    });
  });

  it("points an incomplete dashboard at the next missing setup area", () => {
    const state = setupGuideStateFromDashboard(
      dashboardItem({
        goal: {
          current_saved_cents: 40000,
          id: "goal-1",
          name: "Hospital bill",
          target_cents: 400000,
          target_date: "2026-09-27",
        },
        missing_inputs: ["financial_profile"],
      }),
    );

    expect(state).toEqual({
      activeStep: "profile",
      completedSteps: ["goal"],
    });
  });
});

function financialProfile(overrides: Partial<FinancialProfileResponse> = {}): FinancialProfileResponse {
  return {
    balance_as_of_date: "2026-08-27",
    created_at: "2026-08-27T00:00:00Z",
    id: "profile-1",
    reserve_buffer_cents: 0,
    reserve_buffer_confirmed: false,
    starting_cash_cents: 0,
    updated_at: "2026-08-27T00:00:00Z",
    ...overrides,
  };
}

function incomeSource(overrides: Partial<IncomeSourceResponse> = {}): IncomeSourceResponse {
  return {
    active: true,
    amount_cents: 100000,
    confidence: "confirmed",
    created_at: "2026-08-27T00:00:00Z",
    frequency: "once",
    id: "income-1",
    name: "Paycheck",
    next_date: "2026-08-28",
    updated_at: "2026-08-27T00:00:00Z",
    ...overrides,
  };
}

function plannedExpense(overrides: Partial<PlannedExpenseResponse> = {}): PlannedExpenseResponse {
  return {
    active: true,
    amount_cents: 5000,
    classification: "must_pay",
    created_at: "2026-08-27T00:00:00Z",
    frequency: "once",
    id: "expense-1",
    name: "Bill",
    next_date: "2026-08-29",
    updated_at: "2026-08-27T00:00:00Z",
    ...overrides,
  };
}

function dashboardItem(overrides: Partial<DashboardItem> = {}): DashboardItem {
  return {
    calculated_at: null,
    changed_from_previous: null,
    explanation: null,
    formula_version: null,
    goal: null,
    missing_inputs: [],
    pace: null,
    snapshot_id: null,
    status: "needs_setup",
    ...overrides,
  };
}
