import { api } from "@/shared/api";

export function sendReportsByEmail(reportData: { reportIds: string[] }) {
  // TODO: update request and add validation
  return api.post(`users/me/reports/email`, {
    json: { reportIds: reportData.reportIds },
  });
}

export function sendReportsByTelegram(reportData: { reportIds: string[] }) {
  // TODO: update request and add validation
  return api.post(`users/me/reports/telegram`, {
    json: { reportIds: reportData.reportIds },
  });
}
