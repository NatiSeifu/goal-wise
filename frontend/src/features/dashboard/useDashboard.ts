import { useEffect, useState } from "react";

import { getDashboard } from "../../api/resources.ts";
import type { DashboardItem } from "../../api/types.ts";

type DashboardLoadState =
  | { data: DashboardItem; error: null; status: "ready" }
  | { data: null; error: string; status: "error" }
  | { data: null; error: null; status: "loading" };

export function useDashboard() {
  const [state, setState] = useState<DashboardLoadState>({
    data: null,
    error: null,
    status: "loading",
  });

  useEffect(() => {
    let isCurrent = true;

    async function loadDashboard() {
      try {
        const response = await getDashboard();
        if (isCurrent) {
          setState({ data: response.item, error: null, status: "ready" });
        }
      } catch (error) {
        if (isCurrent) {
          setState({
            data: null,
            error: error instanceof Error ? error.message : "Dashboard data could not be loaded.",
            status: "error",
          });
        }
      }
    }

    void loadDashboard();

    return () => {
      isCurrent = false;
    };
  }, []);

  return state;
}
