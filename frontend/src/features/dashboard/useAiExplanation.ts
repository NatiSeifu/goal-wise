import { useMutation } from "@tanstack/react-query";

import { requestLatestAIExplanation } from "../../api/resources.ts";

export function useAiExplanation() {
  return useMutation({ mutationFn: requestLatestAIExplanation });
}
