import { useMutation } from "@tanstack/react-query";

import { queryClient } from "@/shared/api";

import { updateProjectName } from "./requests";

export function useProjectNameMutation() {
  return useMutation({
    mutationFn: updateProjectName,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["projects"] }),
  });
}
