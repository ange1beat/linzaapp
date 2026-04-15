import React from "react";

import cn from "classnames";
import { SubmitHandler, useController, useForm } from "react-hook-form";
import { Trans, useTranslation } from "react-i18next";

import { ROUTES } from "../../../../shared/config/routes";
import Button from "../../../../shared/ui/button";
import InputPassword from "../../../../shared/ui/inputPassword";
import Link from "../../../../shared/ui/link";
import WindowFrame from "../../../../shared/ui/windowFrame";

import styles from "./UpdatePasswordEntity.module.scss";

interface IFormData {
  currentPassword: string;
  newPassword: string;
  confirmPassword: string;
}

interface IUpdatePasswordEntityProps {
  className?: string;
  errors: IFormData;
  isLoad: boolean;
  onSubmit: (formData: IFormData) => void;
  onChange: (formData: IFormData) => void;
}

function UpdatePasswordEntity({
  className,
  errors,
  isLoad,
  onSubmit,
  onChange,
}: IUpdatePasswordEntityProps) {
  const { t } = useTranslation("entities.updatePassword");
  const { handleSubmit, watch, control } = useForm<IFormData>();
  const submit: SubmitHandler<IFormData> = (data) => onSubmit(data);
  const { field: currentPassword } = useController({
    name: "currentPassword",
    control: control,
  });
  const { field: newPassword } = useController({
    name: "newPassword",
    control: control,
  });
  const { field: confirmPassword } = useController({
    name: "confirmPassword",
    control: control,
  });

  const onChangeHandler = () => {
    const value = watch();
    onChange(value);
  };

  const classes = cn(styles["update-password-entity"], className);
  return (
    <WindowFrame className={classes} title={<Trans i18nKey="title" t={t} />}>
      <form
        className={styles["update-password-entity__form"]}
        onChange={onChangeHandler}
        onSubmit={handleSubmit(submit)}
        name="UpdatePasswordForm"
      >
        <div className={styles["update-password-entity__container"]}>
          <div className={styles["update-password-entity__fields"]}>
            <InputPassword
              name="currentPassword"
              ref={currentPassword.ref}
              value={currentPassword.value ?? ""}
              disabled={isLoad}
              isError={!!errors.currentPassword}
              errorMessage={errors.currentPassword}
              placeholder={t("current-password-placeholder")}
              onChange={currentPassword.onChange}
            />
            <InputPassword
              name="newPassword"
              ref={newPassword.ref}
              value={newPassword.value ?? ""}
              disabled={isLoad}
              isError={!!errors.newPassword}
              errorMessage={errors.newPassword}
              placeholder={t("new-password-placeholder")}
              onChange={newPassword.onChange}
            />
            <InputPassword
              name="confirmPassword"
              ref={confirmPassword.ref}
              value={confirmPassword.value ?? ""}
              disabled={isLoad}
              isError={!!errors.confirmPassword}
              errorMessage={errors.confirmPassword}
              placeholder={t("confirm-password-placeholder")}
              onChange={confirmPassword.onChange}
            />
          </div>
          <Button
            className={styles["update-password-entity__update-button"]}
            view="action"
            width="max"
            type="submit"
            loading={isLoad}
          >
            {t("update-password")}
          </Button>
          <Link
            className={styles["update-password-entity__back-link"]}
            href={ROUTES.dashboard}
          >
            {t("return-to-dashboard")}
          </Link>
        </div>
      </form>
    </WindowFrame>
  );
}

export default UpdatePasswordEntity;
