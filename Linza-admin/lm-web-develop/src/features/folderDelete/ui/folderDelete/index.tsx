import React from "react";

import { useTranslation } from "react-i18next";

import { IFolder, useDeleteFolderMutation } from "@/entities/folders";
import { Button, ModalWindow, Text, useAlert } from "@/shared/ui";

import styles from "./FolderDelete.module.scss";

function FolderDelete({
  folder,
  isOpen,
  projectId,
  onCancel,
}: {
  folder: IFolder;
  isOpen: boolean;
  projectId: string;
  onCancel: () => void;
}) {
  const { t } = useTranslation("features.folderDelete");
  const deleteFolderMutation = useDeleteFolderMutation();
  const { addAlert } = useAlert();

  const onDeleteFolder = () =>
    deleteFolderMutation
      .mutateAsync({ projectId: projectId, folderId: folder.id })
      .then(() => {
        addAlert({
          title: t("success-alert.title"),
          message: t("success-alert.message", { folderName: folder.name }),
          theme: "success",
        });
        onCancel();
      })
      .catch(() => {
        addAlert({
          title: t("error-alert.title"),
          message: t("error-alert.message"),
          theme: "danger",
        });
      });
  return (
    <ModalWindow isOpen={isOpen} title={t("title")} onClose={onCancel}>
      <div className={styles.content}>
        <Text variant="body-2">{t("content")}</Text>
        <Text variant="body-3">{folder.name}</Text>
      </div>
      <div className={styles["buttons-wrapper"]}>
        <Button
          loading={deleteFolderMutation.isPending}
          className={styles["buttons-wrapper__action-button"]}
          view="action"
          onClick={onDeleteFolder}
        >
          {t("button-action")}
        </Button>
        <Button
          loading={deleteFolderMutation.isPending}
          view="normal"
          onClick={onCancel}
        >
          {t("button-cancel")}
        </Button>
      </div>
    </ModalWindow>
  );
}

export default FolderDelete;
