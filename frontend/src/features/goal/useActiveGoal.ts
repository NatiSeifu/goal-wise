import { useQuery } from "@tanstack/react-query";

import { queryKeys } from "../../api/queryKeys.ts";
import { getActiveGoal } from "../../api/resources.ts";
import type { GoalResponse } from "../../api/types.ts";

type ActiveGoalLoadState =
  | { data: GoalResponse | null; error: null; status: "ready" }
  | { data: null; error: string; status: "error" }
  | { data: null; error: null; status: "loading" };

export function useActiveGoal() {
  const query = useQuery({
    queryFn: getActiveGoal,
    queryKey: queryKeys.activeGoal,
  });

  if (query.isPending) {
    return {
      data: null,
      error: null,
      reload: query.refetch,
      status: "loading",
    } satisfies ActiveGoalLoadState & { reload: typeof query.refetch };
  }

  if (query.isError) {
    return {
      data: null,
      error: query.error instanceof Error ? query.error.message : "Goal could not be loaded.",
      reload: query.refetch,
      status: "error",
    } satisfies ActiveGoalLoadState & { reload: typeof query.refetch };
  }

  return {
    data: query.data.item,
    error: null,
    reload: query.refetch,
    status: "ready",
  } satisfies ActiveGoalLoadState & { reload: typeof query.refetch };
}
