import { useMutation } from "@tanstack/react-query";

import { queryClient } from "@/shared/api";

import { deleteProjectReports } from "./requests";

export function useDeleteProjectReportsMutation(projectId: string) {
  return useMutation({
    mutationFn: deleteProjectReports,
    onSuccess: () =>
      queryClient.invalidateQueries({
        queryKey: ["reports", { projectId }],
      }),
  });
}
