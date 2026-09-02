import { apiRequest } from "./client.ts";
import { endpoints } from "./endpoints.ts";
import type {
  CalculationSnapshotItemResponse,
  AIExplanationItemResponse,
  AIExplanationAvailabilityResponse,
  DashboardResponse,
  FinancialProfileItemResponse,
  FinancialProfileRequest,
  GoalItemResponse,
  GoalRequest,
  IncomeSourceItemResponse,
  IncomeSourceListResponse,
  IncomeSourceRequest,
  PlannedExpenseItemResponse,
  PlannedExpenseListResponse,
  PlannedExpenseRequest,
  PlanningImportConfirmResponse,
  PlanningImportPreviewResponse,
} from "./types.ts";

export function getDashboard() {
  return apiRequest<DashboardResponse>(endpoints.dashboard);
}

export function getLatestCalculationSnapshot() {
  return apiRequest<CalculationSnapshotItemResponse>(endpoints.calculationSnapshots.latest);
}

export function requestLatestAIExplanation() {
  return apiRequest<AIExplanationItemResponse>(endpoints.aiExplanations.latest, {
    method: "POST",
  });
}

export function getAIExplanationStatus() {
  return apiRequest<AIExplanationAvailabilityResponse>(endpoints.aiExplanations.status);
}

export function getActiveGoal() {
  return apiRequest<GoalItemResponse>(endpoints.goals.active);
}

export function createGoal(payload: GoalRequest) {
  return apiRequest<GoalItemResponse>(endpoints.goals.collection, {
    method: "POST",
    body: payload,
  });
}

export function updateGoal(goalId: string, payload: GoalRequest) {
  return apiRequest<GoalItemResponse>(endpoints.goals.item(goalId), {
    method: "PATCH",
    body: payload,
  });
}

export function archiveGoal(goalId: string) {
  return apiRequest<GoalItemResponse>(endpoints.goals.archive(goalId), {
    method: "POST",
  });
}

export function getFinancialProfile() {
  return apiRequest<FinancialProfileItemResponse>(endpoints.financialProfile);
}

export function putFinancialProfile(payload: FinancialProfileRequest) {
  return apiRequest<FinancialProfileItemResponse>(endpoints.financialProfile, {
    method: "PUT",
    body: payload,
  });
}

export function listIncomeSources() {
  return apiRequest<IncomeSourceListResponse>(endpoints.incomeSources.collection);
}

export function createIncomeSource(payload: IncomeSourceRequest) {
  return apiRequest<IncomeSourceItemResponse>(endpoints.incomeSources.collection, {
    method: "POST",
    body: payload,
  });
}

export function updateIncomeSource(incomeSourceId: string, payload: IncomeSourceRequest) {
  return apiRequest<IncomeSourceItemResponse>(endpoints.incomeSources.item(incomeSourceId), {
    method: "PATCH",
    body: payload,
  });
}

export function deleteIncomeSource(incomeSourceId: string) {
  return apiRequest<void>(endpoints.incomeSources.item(incomeSourceId), {
    method: "DELETE",
  });
}

export function listPlannedExpenses() {
  return apiRequest<PlannedExpenseListResponse>(endpoints.plannedExpenses.collection);
}

export function createPlannedExpense(payload: PlannedExpenseRequest) {
  return apiRequest<PlannedExpenseItemResponse>(endpoints.plannedExpenses.collection, {
    method: "POST",
    body: payload,
  });
}

export function updatePlannedExpense(plannedExpenseId: string, payload: PlannedExpenseRequest) {
  return apiRequest<PlannedExpenseItemResponse>(endpoints.plannedExpenses.item(plannedExpenseId), {
    method: "PATCH",
    body: payload,
  });
}

export function deletePlannedExpense(plannedExpenseId: string) {
  return apiRequest<void>(endpoints.plannedExpenses.item(plannedExpenseId), {
    method: "DELETE",
  });
}

export function previewPlanningImport(file: File) {
  const body = new FormData();
  body.append("file", file);
  return apiRequest<PlanningImportPreviewResponse>(endpoints.planningImport.preview, {
    method: "POST",
    body,
  });
}

export function confirmPlanningImport(previewToken: string) {
  return apiRequest<PlanningImportConfirmResponse>(endpoints.planningImport.confirm, {
    method: "POST",
    body: { preview_token: previewToken },
  });
}
