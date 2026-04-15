import React from "react";

import { useTranslation } from "react-i18next";

import { IProject } from "@/entities/projects";
import { Button, Input, ModalWindow, useAlert } from "@/shared/ui";

import { useProjectAddMutation } from "../../api/queries";
import { useNameForm } from "../../models/forms";

import styles from "./ProjectAdd.module.scss";

export default function ProjectAdd({
  isOpen,
  onClose,
  onSuccess,
}: {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (id: IProject) => void;
}) {
  const { t } = useTranslation(["features.projectAdd", "errors", "controls"]);
  const { handleSubmit, nameField, setError, errors, reset } = useNameForm();
  const projectAddMutation = useProjectAddMutation();
  const { addAlert } = useAlert();

  const onSubmitHandler = handleSubmit((data) => {
    projectAddMutation
      .mutateAsync({ name: data.name })
      .then(onSuccess)
      .catch((response) => {
        if (response.status === 400) {
          setError("name", {
            type: "custom",
            message: response.errors.name,
          });
        }
        if (response.status === 409) {
          setError("name", {
            type: "custom",
            message: "project.conflict-project-name-error",
          });
        } else {
          addAlert({
            title: t("title", { ns: "errors" }),
            message: t("server-error", { ns: "errors" }),
            theme: "danger",
          });
        }
      });
  });

  const onCloseHandler = () => {
    reset();
    onClose();
  };

  const isLoading = projectAddMutation.isPending;
  return (
    <ModalWindow isOpen={isOpen} title={t("title")} onClose={onCloseHandler}>
      <form onSubmit={onSubmitHandler}>
        <div className={styles["project-add__input"]}>
          <Input
            value={nameField.value}
            ref={nameField.ref}
            isError={!!errors.name}
            errorMessage={t(errors.name?.message ?? "", { ns: "errors" })}
            placeholder={t("placeholder")}
            size="xl"
            disabled={isLoading}
            onChange={nameField.onChange}
          />
        </div>
        <div className={styles["project-add__button"]}>
          <Button loading={isLoading} view="normal" onClick={onCloseHandler}>
            {t("cancel", { ns: "controls" })}
          </Button>
          <Button loading={isLoading} view="action" type="submit">
            {t("apply", { ns: "controls" })}
          </Button>
        </div>
      </form>
    </ModalWindow>
  );
}
