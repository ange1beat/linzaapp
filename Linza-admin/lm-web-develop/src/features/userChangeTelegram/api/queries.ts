import { useMutation } from "@tanstack/react-query";

import { queryClient } from "@/shared/api";

import { updateUserTelegram } from "./requests";

export function useTelegramMutation() {
  return useMutation({
    mutationFn: updateUserTelegram,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["user"] }),
  });
}
