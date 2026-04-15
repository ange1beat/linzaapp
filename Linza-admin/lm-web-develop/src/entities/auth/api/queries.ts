import { useMutation } from "@tanstack/react-query";

import { sendOtpByEmail, sendOtpBySMS } from "./requests";

export function useSendOtpByEmail() {
  return useMutation({
    mutationFn: sendOtpByEmail,
  });
}

export function useSendOtpBySMS() {
  return useMutation({
    mutationFn: sendOtpBySMS,
  });
}
