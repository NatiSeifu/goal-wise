import { useMutation, useQuery } from "@tanstack/react-query";

import { getAIExplanationStatus, requestLatestAIExplanation } from "../../api/resources.ts";
import { queryKeys } from "../../api/queryKeys.ts";

export function useAiExplanationAvailability() {
  return useQuery({
    queryFn: getAIExplanationStatus,
    queryKey: queryKeys.aiExplanationStatus,
  });
}

export function useAiExplanation() {
  return useMutation({ mutationFn: requestLatestAIExplanation });
}
