import { useEffect, useState } from "react";

import { getActiveGoal } from "../../api/resources.ts";
import type { GoalResponse } from "../../api/types.ts";

type ActiveGoalLoadState =
  | { data: GoalResponse | null; error: null; status: "ready" }
  | { data: null; error: string; status: "error" }
  | { data: null; error: null; status: "loading" };

export function useActiveGoal() {
  const [state, setState] = useState<ActiveGoalLoadState>({
    data: null,
    error: null,
    status: "loading",
  });

  async function reload() {
    setState({ data: null, error: null, status: "loading" });
    try {
      const response = await getActiveGoal();
      setState({ data: response.item, error: null, status: "ready" });
    } catch (error) {
      setState({
        data: null,
        error: error instanceof Error ? error.message : "Goal could not be loaded.",
        status: "error",
      });
    }
  }

  useEffect(() => {
    void reload();
  }, []);

  return { ...state, reload };
}
