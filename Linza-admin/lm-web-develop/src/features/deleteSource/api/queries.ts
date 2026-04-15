import { useMutation } from "@tanstack/react-query";

import { deleteSourceById } from "./requests";
import { queryClient } from "@/shared/api";

export function useDeleteSourceByIdMutation() {
  return useMutation({
    mutationFn: deleteSourceById,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["sources"] }),
  });
}
