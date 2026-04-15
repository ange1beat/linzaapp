import React from "react";

import cn from "classnames";
import { Controller, SubmitHandler, useForm } from "react-hook-form";
import { Trans } from "react-i18next";
import { useTranslation } from "react-i18next";

import { Button, KeyField, Text, WindowFrame } from "@/shared/ui";

import { LoginType } from "../../models";

import styles from "./ConfirmCodeForResetPasswordEntity.module.scss";

interface IConfirmCodeEntityProps {
  error: string;
  children: React.ReactNode;
  onSubmit: (otpValue: string) => void;
  onBack: () => void;
  className?: string;
  loginType: LoginType;
  loading: boolean;
}

interface IFormData {
  otpValue: string;
}

function ConfirmCodeForResetPasswordEntity({
  error,
  children,
  onSubmit,
  onBack,
  className,
  loading,
  loginType,
}: IConfirmCodeEntityProps) {
  const { t } = useTranslation("entities.ConfirmCodeForResetPassword");
  const { handleSubmit, control } = useForm<IFormData>();
  const submit: SubmitHandler<IFormData> = (data) => onSubmit(data.otpValue);

  const text =
    loginType === "phone" ? "info-message-phone" : "info-message-email";
  const classes = cn(styles["confirm-code-entity"], className);
  return (
    <WindowFrame className={classes} title={<Trans i18nKey="title" t={t} />}>
      <form
        className={styles["confirm-code-entity__form"]}
        onSubmit={handleSubmit(submit)}
      >
        <div className={styles["confirm-code-entity__container"]}>
          <Text variant="body-3">
            <Trans i18nKey={text} t={t} />
          </Text>
          <Controller
            name="otpValue"
            render={({ field }) => {
              return (
                <KeyField
                  onChange={field.onChange}
                  isError={!!error}
                  errorMessage={error}
                  disabled={field.disabled || loading}
                  autoFocus
                />
              );
            }}
            control={control}
          />
          {children}
          <div className={styles["confirm-code-entity__buttons"]}>
            <Button
              view="action"
              onClick={() => {}}
              loading={loading}
              type="submit"
              className={styles["confirm-code-entity__button"]}
            >
              {t("verifyOtpCodeBtnTitle")}
            </Button>
            <Button onClick={onBack} view="normal">
              {t("button-back")}
            </Button>
          </div>
        </div>
      </form>
    </WindowFrame>
  );
}

export default ConfirmCodeForResetPasswordEntity;
