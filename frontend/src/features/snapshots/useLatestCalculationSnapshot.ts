import { useEffect, useState } from "react";

import { getLatestCalculationSnapshot } from "../../api/resources.ts";
import type { CalculationSnapshotResponse } from "../../api/types.ts";

type SnapshotLoadState =
  | { data: CalculationSnapshotResponse | null; error: null; status: "ready" }
  | { data: null; error: string; status: "error" }
  | { data: null; error: null; status: "loading" };

export function useLatestCalculationSnapshot() {
  const [state, setState] = useState<SnapshotLoadState>({
    data: null,
    error: null,
    status: "loading",
  });

  useEffect(() => {
    let isCurrent = true;

    async function loadSnapshot() {
      try {
        const response = await getLatestCalculationSnapshot();
        if (isCurrent) {
          setState({ data: response.item, error: null, status: "ready" });
        }
      } catch (error) {
        if (isCurrent) {
          setState({
            data: null,
            error: error instanceof Error ? error.message : "Snapshot data could not be loaded.",
            status: "error",
          });
        }
      }
    }

    void loadSnapshot();

    return () => {
      isCurrent = false;
    };
  }, []);

  return state;
}
