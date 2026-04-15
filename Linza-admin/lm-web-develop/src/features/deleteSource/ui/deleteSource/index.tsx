import React from "react";

import { useTranslation } from "react-i18next";

import { ISource } from "@/entities/sources/models/types";
import { useDeleteSourceByIdMutation } from "@/features/deleteSource/api/queries";
import { Button, ModalWindow, Text, useAlert } from "@/shared/ui";

import styles from "./DeleteSource.module.scss";

interface IProps {
  isOpen: boolean;
  source: ISource;
  onClose: () => void;
}

function DeleteSourceFeature({ isOpen, source, onClose }: IProps) {
  const { t } = useTranslation("features.deleteSource");
  const deleteSourceById = useDeleteSourceByIdMutation();
  const { addAlert } = useAlert();

  const onDeleteSource = () =>
    deleteSourceById
      .mutateAsync(source.id)
      .then(() => {
        addAlert({
          title: t("success-alert.title"),
          message: t("success-alert.message"),
          theme: "success",
        });
        onClose();
      })
      .catch(() => {
        addAlert({
          title: t("error-alert.title"),
          message: t("error-alert.message"),
          theme: "danger",
        });
        onClose();
      });

  return (
    <ModalWindow isOpen={isOpen} title={t("title")} onClose={onClose}>
      <div className={styles.content}>
        <Text variant="body-2">{t("content")}</Text>
        <Text variant="body-3">{source.url}</Text>
      </div>
      <div className={styles["buttons-wrapper"]}>
        <Button
          loading={deleteSourceById.isPending}
          className={styles["buttons-wrapper__action-button"]}
          view="action"
          onClick={onDeleteSource}
        >
          {t("button-action")}
        </Button>
        <Button
          loading={deleteSourceById.isPending}
          view="normal"
          onClick={onClose}
        >
          {t("button-cancel")}
        </Button>
      </div>
    </ModalWindow>
  );
}

export default DeleteSourceFeature;
