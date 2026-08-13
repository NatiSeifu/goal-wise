import { useEffect, useState } from "react";

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
  const [state, setState] = useState<FinancialInputsLoadState>({
    data: null,
    error: null,
    status: "loading",
  });

  async function reload() {
    setState({ data: null, error: null, status: "loading" });
    try {
      const [profileResponse, incomeResponse, expenseResponse] = await Promise.all([
        getFinancialProfile(),
        listIncomeSources(),
        listPlannedExpenses(),
      ]);
      setState({
        data: {
          expenses: expenseResponse.items,
          incomeSources: incomeResponse.items,
          profile: profileResponse.item,
        },
        error: null,
        status: "ready",
      });
    } catch (error) {
      setState({
        data: null,
        error: error instanceof Error ? error.message : "Financial inputs could not be loaded.",
        status: "error",
      });
    }
  }

  useEffect(() => {
    void reload();
  }, []);

  return { ...state, reload };
}
