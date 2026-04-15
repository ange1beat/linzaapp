import { useMutation } from "@tanstack/react-query";

import { queryClient } from "@/shared/api";

import { deleteProject } from "./requests";

export function useDeleteProject() {
  return useMutation({
    mutationFn: deleteProject,
    onSuccess: () =>
      queryClient.invalidateQueries({
        queryKey: ["projects", "list"],
      }),
  });
}
