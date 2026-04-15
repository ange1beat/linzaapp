import { useMutation } from "@tanstack/react-query";

import { queryClient } from "@/shared/api";

import { toggleParsingDataSource } from "./requests";

export function useToggleParsingDataSource() {
  return useMutation({
    mutationFn: toggleParsingDataSource,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["sources"] });
    },
  });
}
