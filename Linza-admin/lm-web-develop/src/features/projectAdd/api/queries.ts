import { useMutation } from "@tanstack/react-query";

import { queryClient } from "@/shared/api";

import { addProject } from "./requests";

export function useProjectAddMutation() {
  return useMutation({
    mutationFn: addProject,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects", "detail"] });
    },
  });
}
