import { useMutation } from "@tanstack/react-query";

import { getAuthToken } from "@/entities/session";

import {
  authorizeUser,
  sendConfirmCode,
  sendVerificationOtpResponse,
} from "./requests";

export function useAuthorizeUser() {
  return useMutation({
    mutationFn: authorizeUser,
  });
}

export function useConfirmCode() {
  return useMutation({
    mutationFn: sendConfirmCode,
  });
}

export function useSendOtpCodeForVerify() {
  return useMutation({
    mutationFn: sendVerificationOtpResponse,
  });
}

export function useGetAuthToken() {
  return useMutation({
    mutationFn: getAuthToken,
  });
}
