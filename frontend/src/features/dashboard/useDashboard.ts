import { useQuery } from "@tanstack/react-query";

import { queryKeys } from "../../api/queryKeys.ts";
import { getDashboard } from "../../api/resources.ts";
import type { DashboardItem } from "../../api/types.ts";

type DashboardLoadState =
  | { data: DashboardItem; error: null; status: "ready" }
  | { data: null; error: string; status: "error" }
  | { data: null; error: null; status: "loading" };

export function useDashboard() {
  const query = useQuery({
    queryFn: getDashboard,
    queryKey: queryKeys.dashboard,
  });

  if (query.isPending) {
    return { data: null, error: null, status: "loading" } satisfies DashboardLoadState;
  }

  if (query.isError) {
    return {
      data: null,
      error: query.error instanceof Error ? query.error.message : "Dashboard data could not be loaded.",
      status: "error",
    } satisfies DashboardLoadState;
  }

  return { data: query.data.item, error: null, status: "ready" } satisfies DashboardLoadState;
}
