import { useQuery } from "@tanstack/react-query";

import { queryKeys } from "../../api/queryKeys.ts";
import { getFinancialProfile, listIncomeSources, listPlannedExpenses } from "../../api/resources.ts";
import type {
  FinancialProfileResponse,
  IncomeSourceResponse,
  PlannedExpenseResponse,
} from "../../api/types.ts";

type FinancialInputsData = {
  expenses: PlannedExpenseResponse[];
  incomeSources: IncomeSourceResponse[];
  profile: FinancialProfileResponse | null;
};

type FinancialInputsLoadState =
  | { data: FinancialInputsData; error: null; status: "ready" }
  | { data: null; error: string; status: "error" }
  | { data: null; error: null; status: "loading" };

export function useFinancialInputs() {
  const query = useQuery({
    queryFn: async () => {
      const [profileResponse, incomeResponse, expenseResponse] = await Promise.all([
        getFinancialProfile(),
        listIncomeSources(),
        listPlannedExpenses(),
      ]);
      return {
        expenses: expenseResponse.items,
        incomeSources: incomeResponse.items,
        profile: profileResponse.item,
      };
    },
    queryKey: queryKeys.financialInputs,
  });

  if (query.isPending) {
    return {
      data: null,
      error: null,
      reload: query.refetch,
      status: "loading",
    } satisfies FinancialInputsLoadState & { reload: typeof query.refetch };
  }

  if (query.isError) {
    return {
      data: null,
      error: query.error instanceof Error ? query.error.message : "Financial inputs could not be loaded.",
      reload: query.refetch,
      status: "error",
    } satisfies FinancialInputsLoadState & { reload: typeof query.refetch };
  }

  return {
    data: query.data,
    error: null,
    reload: query.refetch,
    status: "ready",
  } satisfies FinancialInputsLoadState & { reload: typeof query.refetch };
}
