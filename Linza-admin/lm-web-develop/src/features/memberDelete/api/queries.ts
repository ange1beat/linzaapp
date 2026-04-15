import { useMutation } from "@tanstack/react-query";

import { queryClient } from "@/shared/api";

import { deleteMember } from "./requests";

export function useDeleteMember() {
  return useMutation({
    mutationFn: deleteMember,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["members"] });
    },
  });
}
