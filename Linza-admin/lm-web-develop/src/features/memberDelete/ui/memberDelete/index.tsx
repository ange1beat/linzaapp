import React from "react";

import { useTranslation } from "react-i18next";

import { IMember } from "@/entities/members/models/models";
import { getFullName } from "@/shared/lib";
import { Button, ModalWindow, useAlert, Text } from "@/shared/ui";

import { useDeleteMember } from "../../api/queries";

import styles from "./DeleteMember.module.scss";

type IPropsDeleteProject = {
  member: Pick<IMember, "id" | "firstName" | "lastName">;
  onCancel: () => void;
  onSuccess: () => void;
  isOpen: boolean;
};

export default function MemberDelete({
  member,
  onSuccess,
  onCancel,
  isOpen,
}: IPropsDeleteProject) {
  const { t } = useTranslation(["features.memberDelete", "errors"]);
  const deleteMember = useDeleteMember();
  const fullName = getFullName(member);
  const { addAlert } = useAlert();

  const onDeleteProject = () => {
    deleteMember
      .mutateAsync(member)
      .then(() => {
        addAlert({
          title: t("success-alert.title"),
          theme: "success",
          message: t("success-alert.content", {
            username: fullName,
          }),
        });
        onSuccess();
      })
      .catch(() => {
        addAlert({
          title: t("title", { ns: "errors" }),
          message: t("server-error", { ns: "errors" }),
          theme: "danger",
        });
        onCancel();
      });
  };
  return (
    <ModalWindow isOpen={isOpen} title={t("title")} onClose={onCancel}>
      <div className={styles.content}>
        <Text variant="body-2">{t("content")}</Text>
        <Text variant="body-3">{fullName}</Text>
      </div>
      <div className={styles["buttons-wrapper"]}>
        <Button
          loading={deleteMember.isPending}
          className={styles["buttons-wrapper__action-button"]}
          view="action"
          onClick={onDeleteProject}
        >
          {t("button-action")}
        </Button>
        <Button
          loading={deleteMember.isPending}
          view="normal"
          onClick={onCancel}
        >
          {t("button-cancel")}
        </Button>
      </div>
    </ModalWindow>
  );
}
