import React from "react";

import { Trans, useTranslation } from "react-i18next";

import { Button, ModalWindow, Text, useAlert, Label } from "@/shared/ui";

import { useDeleteProjectReportsMutation } from "../../api/queries";

import styles from "./ProjectReportsDelete.module.scss";

function ProjectReportsDelete({
  reports,
  projectId,
  isOpen,
  onClose,
}: {
  projectId: string;
  reports: { id: string; name: string }[];
  isOpen: boolean;
  onClose: () => void;
}) {
  const { t } = useTranslation(["features.reportsDelete", "errors"]);
  const deleteProjectReportsMutation =
    useDeleteProjectReportsMutation(projectId);
  const { addAlert } = useAlert();

  const onDeleteProjectReports = () => {
    deleteProjectReportsMutation
      .mutateAsync({
        projectId: projectId,
        reportIds: reports.map((r) => r.id),
      })
      .then(() => {
        addAlert({
          title: t("success-alert.title", {
            ns: "features.reportsDelete",
          }),
          message: t("success-alert.content", {
            ns: "features.reportsDelete",
          }),
          theme: "success",
        });
        onClose();
      })
      .catch(() => {
        addAlert({
          title: t("title", { ns: "errors" }),
          message: t("server-error", { ns: "errors" }),
          theme: "danger",
        });
      });
  };

  return (
    <ModalWindow
      isOpen={isOpen}
      title={t("title", { ns: "features.reportsDelete" })}
      onClose={onClose}
    >
      <div className={styles.content}>
        <Text variant="body-2">
          <Trans>
            {t("content", {
              ns: "features.reportsDelete",
              count: reports.length > 6 ? reports.length : undefined,
            })}
          </Trans>
        </Text>

        {reports.length <= 6 && (
          <div className={styles["project-reports"]}>
            {reports.map((report) => (
              <Label
                size="m"
                theme="normal"
                className={styles["project-reports__report"]}
                key={`report-${report.id}`}
              >
                {report.name}
              </Label>
            ))}
          </div>
        )}
      </div>
      <div className={styles["buttons-wrapper"]}>
        <Button
          loading={deleteProjectReportsMutation.isPending}
          className={styles["buttons-wrapper__action-button"]}
          view="action"
          onClick={onDeleteProjectReports}
        >
          {t("button-action", { ns: "features.reportsDelete" })}
        </Button>
        <Button
          loading={deleteProjectReportsMutation.isPending}
          view="normal"
          onClick={onClose}
        >
          {t("button-cancel", { ns: "features.reportsDelete" })}
        </Button>
      </div>
    </ModalWindow>
  );
}

export default ProjectReportsDelete;
