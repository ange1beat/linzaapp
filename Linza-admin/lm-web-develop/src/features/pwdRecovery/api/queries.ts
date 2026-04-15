import { useMutation } from "@tanstack/react-query";

import {
  recoveryPWDByEmail,
  recoveryPWDBySMS,
  recoveryVerify,
  setPassword,
} from "./requests";

export function useRecoveryPDWByEmail() {
  return useMutation({
    mutationFn: recoveryPWDByEmail,
  });
}

export function useRecoveryPDWBySMS() {
  return useMutation({
    mutationFn: recoveryPWDBySMS,
  });
}

export function useRecoveryVerifyMutation() {
  return useMutation({
    mutationFn: recoveryVerify,
  });
}

export function usePasswordMutation() {
  return useMutation({
    mutationFn: setPassword,
  });
}
