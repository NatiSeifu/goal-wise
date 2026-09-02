import { useQuery } from "@tanstack/react-query";

import { queryKeys } from "../../api/queryKeys.ts";
import { getLatestCalculationSnapshot } from "../../api/resources.ts";
import type { CalculationSnapshotResponse } from "../../api/types.ts";

type SnapshotLoadState =
  | { data: CalculationSnapshotResponse | null; error: null; status: "ready" }
  | { data: null; error: string; status: "error" }
  | { data: null; error: null; status: "loading" };

export function useLatestCalculationSnapshot() {
  const query = useQuery({
    queryFn: getLatestCalculationSnapshot,
    queryKey: queryKeys.latestCalculationSnapshot,
  });

  if (query.isPending) {
    return { data: null, error: null, status: "loading" } satisfies SnapshotLoadState;
  }

  if (query.isError) {
    return {
      data: null,
      error: query.error instanceof Error ? query.error.message : "Snapshot data could not be loaded.",
      status: "error",
    } satisfies SnapshotLoadState;
  }

  return { data: query.data.item, error: null, status: "ready" } satisfies SnapshotLoadState;
}
