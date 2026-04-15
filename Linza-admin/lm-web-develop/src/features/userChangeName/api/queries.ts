import { useMutation } from "@tanstack/react-query";

import { updateUserName } from "@/features/userChangeName/api/requests";
import { queryClient } from "@/shared/api";

export function useUserNameMutation() {
  return useMutation({
    mutationFn: updateUserName,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["user"] });
    },
  });
}
