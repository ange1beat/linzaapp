import { useTranslation } from "react-i18next";

import { useAlert } from "@/shared/ui";

import { useSendReportsToEmail } from "../api/queries";

export function useReportsSendEmail(reportIds: string[]) {
  const { t } = useTranslation(["features.reportsSend", "errors"]);
  const { addAlert } = useAlert();
  const sendReportsToEmailMutation = useSendReportsToEmail();

  return () =>
    sendReportsToEmailMutation
      .mutateAsync({
        reportIds,
      })
      .then(() =>
        addAlert({
          title: t("success-title", { ns: "features.reportsSend" }),
          message: t("success-message-email", { ns: "features.reportsSend" }),
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
