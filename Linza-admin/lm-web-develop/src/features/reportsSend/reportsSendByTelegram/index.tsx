import { useTranslation } from "react-i18next";

import { useAlert } from "@/shared/ui";

import { useSendReportsToTelegram } from "../api/queries";

export function useReportsSendTelegram(reportIds: string[]) {
  const { t } = useTranslation(["features.reportsSend", "errors"]);
  const { addAlert } = useAlert();
  const sendReportsToTelegramMutation = useSendReportsToTelegram();

  return () =>
    sendReportsToTelegramMutation
      .mutateAsync({
        reportIds,
      })
      .then(() =>
        addAlert({
          title: t("success-title", { ns: "features.reportsSend" }),
          message: t("success-message-telegram", {
            ns: "features.reportsSend",
          }),
          theme: "success",
        }),
      )
      .catch(() =>
        addAlert({
          title: t("title", { ns: "errors" }),
          message: t("server-error", { ns: "errors" }),
          theme: "danger",
        }),
      );
}
