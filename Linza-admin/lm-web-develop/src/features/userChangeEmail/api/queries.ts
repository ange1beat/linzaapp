import { useMutation } from "@tanstack/react-query";

import { queryClient } from "@/shared/api";

import { getChangeEmailOTP, updateUserEmail } from "./requests";

export function useEmailMutation() {
  return useMutation({
    mutationFn: updateUserEmail,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["user"] }),
  });
}

export function useEmailOTPMutation() {
  return useMutation({
    mutationFn: getChangeEmailOTP,
  });
}
