import type {
  DashboardItem,
  FinancialProfileResponse,
  IncomeSourceResponse,
  PlannedExpenseResponse,
} from "../../api/types.ts";
import type { SetupStepId } from "../../components/onboarding/SetupGuide.tsx";

export type SetupGuideState = {
  activeStep: SetupStepId;
  completedSteps: SetupStepId[];
};

export function setupGuideStateFromInputs({
  currentStep,
  expenses,
  hasGoal,
  incomeSources,
  profile,
}: {
  currentStep: SetupStepId;
  expenses: PlannedExpenseResponse[];
  hasGoal: boolean;
  incomeSources: IncomeSourceResponse[];
  profile: FinancialProfileResponse | null;
}): SetupGuideState {
  const completedSteps: SetupStepId[] = [];

  if (hasGoal) {
    completedSteps.push("goal");
  }

  if (profile !== null && profile.reserve_buffer_confirmed) {
    completedSteps.push("profile");
  }

  if (incomeSources.some((source) => source.active)) {
    completedSteps.push("income");
  }

  if (expenses.some((expense) => expense.active)) {
    completedSteps.push("expenses");
  }

  return {
    activeStep: currentStep,
    completedSteps,
  };
}

export function setupGuideStateFromDashboard(item: DashboardItem): SetupGuideState {
  const missingInputs = new Set(item.missing_inputs);
  const completedSteps: SetupStepId[] = [];

  if (item.goal !== null && !missingInputs.has("active_goal")) {
    completedSteps.push("goal");
  }

  if (item.status === "ready" || item.pace !== null) {
    return {
      activeStep: "dashboard",
      completedSteps: ["goal", "profile", "income", "expenses"],
    };
  }

  if (missingInputs.has("active_goal")) {
    return { activeStep: "goal", completedSteps };
  }

  if (missingInputs.has("financial_profile") || missingInputs.has("reserve_buffer_confirmation")) {
    return { activeStep: "profile", completedSteps };
  }

  return {
    activeStep: "dashboard",
    completedSteps: [...completedSteps, "profile"],
  };
}
