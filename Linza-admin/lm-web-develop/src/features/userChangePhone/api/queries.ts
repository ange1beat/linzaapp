import { useMutation } from "@tanstack/react-query";

import { queryClient } from "@/shared/api";

import { getChangePhoneOTP, updateUserPhone } from "./requests";

export function usePhoneMutation() {
  return useMutation({
    mutationFn: updateUserPhone,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["user"] }),
  });
}

export function usePhoneOTPMutation() {
  return useMutation({
    mutationFn: getChangePhoneOTP,
  });
}
