import React from "react";

import { useTranslation } from "react-i18next";

import { IProject } from "@/entities/projects";
import { Button, ModalWindow, Text, useAlert } from "@/shared/ui";

import { useDeleteProject } from "../../api/queries";

import styles from "./ProjectDelete.module.scss";

export default function ProjectDelete({
  project,
  isOpen,
  onClose,
  onSuccess,
}: {
  project: Pick<IProject, "id" | "name">;
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}) {
  const { t } = useTranslation("features.projectDelete");
  const deleteProject = useDeleteProject();
  const { addAlert } = useAlert();

  const onDeleteProject = () => {
    deleteProject
      .mutateAsync(project.id)
      .then(() => {
        onSuccess?.();
        addAlert({
          title: t("success-alert.title"),
          theme: "success",
          message: t("success-alert.content", { projectName: project.name }),
        });
      })
      .catch(() => {
        addAlert({
          title: t("error-alert.title"),
          theme: "danger",
          message: t("error-alert.content"),
        });
      })
      .finally(onClose);
  };

  return (
    <ModalWindow isOpen={isOpen} title={t("title")} onClose={onClose}>
      <div className={styles.content}>
        <Text variant="body-2">{t("content")}</Text>
        <Text variant="body-3">{project.name}</Text>
      </div>
      <div className={styles["buttons-wrapper"]}>
        <Button
          loading={deleteProject.isPending}
          className={styles["buttons-wrapper__action-button"]}
          view="action"
          onClick={onDeleteProject}
        >
          {t("button-action")}
        </Button>
        <Button
          loading={deleteProject.isPending}
          view="normal"
          onClick={onClose}
        >
          {t("button-cancel")}
        </Button>
      </div>
    </ModalWindow>
  );
}
