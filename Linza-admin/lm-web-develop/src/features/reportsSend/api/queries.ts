import { useMutation } from "@tanstack/react-query";

import { sendReportsByEmail, sendReportsByTelegram } from "./requests";

export function useSendReportsToEmail() {
  return useMutation({
    mutationFn: sendReportsByEmail,
  });
}

export function useSendReportsToTelegram() {
  return useMutation({
    mutationFn: sendReportsByTelegram,
  });
}
