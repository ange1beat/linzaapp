import React from "react";

import { zodResolver } from "@hookform/resolvers/zod";
import cn from "classnames";
import { useController, useForm } from "react-hook-form";
import { Trans, useTranslation } from "react-i18next";

import { LoginField, LoginType } from "@/entities/auth";
import { useBackLng } from "@/entities/language";
import { ROUTES } from "@/shared/config";
import { Button, Link, WindowFrame, useAlert } from "@/shared/ui";

import { useRecoveryPDWByEmail, useRecoveryPDWBySMS } from "../../api/queries";
import { sendCodeForResetPasswordSchema } from "../../models/validation";

import styles from "./LoginInput.module.scss";

function LoginInput({
  onClick,
  onError,
  onSuccess,
  className,
}: {
  className?: string;
  onClick?: () => void;
  onSuccess: (login: string, type: LoginType) => void;
  onError?: (errors: { [name: string]: string }) => void;
}) {
  const { t } = useTranslation(["features.loginInput", "errors"]);
  const sendCodeFromEmailMutation = useRecoveryPDWByEmail();
  const sendCodeFromPhoneMutation = useRecoveryPDWBySMS();
  const [loginType, setLoginType] = React.useState<LoginType | undefined>(
    undefined,
  );
  const { addAlert } = useAlert();
  const locale = useBackLng();

  const {
    handleSubmit,
    control,
    formState: { errors },
    setError,
    clearErrors,
  } = useForm<{ login: string }>({
    defaultValues: {
      login: "",
    },
    resolver: zodResolver(sendCodeForResetPasswordSchema),
  });

  const { field: login } = useController({
    name: "login",
    control: control,
  });

  const onChangeFilled = (
    currentLogin: string,
    type: LoginType | undefined,
  ) => {
    login.onChange(currentLogin);
    setLoginType(type);
  };

  const sendCodeHandler = () => {
    clearErrors();
    onClick?.();
    if (loginType === "email") {
      login &&
        sendCodeFromEmailMutation
          .mutateAsync({ email: login.value, locale })
          .then(() => {
            onSuccess(login.value, "email");
          })
          .catch((e) => {
            if (e.status === 500) {
              addAlert({
                title: t("title", { ns: "errors" }),
                message: t("server-error", { ns: "errors" }),
                theme: "danger",
              });
              return;
            } else {
              onError?.(e);
              setError("login", {
                type: "custom",
                message: t("login.invalid", { ns: "errors" }),
              });
            }
          });
    } else if (loginType === "phone") {
      login &&
        sendCodeFromPhoneMutation
          .mutateAsync({ phoneNumber: login.value, locale })
          .then(() => onSuccess(login.value, "phone"))
          .catch((e) => {
            if (e.status === 500) {
              addAlert({
                title: t("title", { ns: "errors" }),
                message: t("server-error", { ns: "errors" }),
                theme: "danger",
              });
              return;
            } else {
              onError?.(e);
              setError("login", {
                type: "custom",
                message: t("login.invalid", { ns: "errors" }),
              });
            }
          });
    } else {
      setError("login", {
        type: "custom",
        message: t("login.invalid", { ns: "errors" }),
      });
    }
  };

  const classes = cn(className, styles["login-input"]);
  return (
    <div className={classes}>
      <WindowFrame
        className={styles["login-input__window"]}
        title={<Trans i18nKey="title" t={t} />}
      >
        <form
          onSubmit={handleSubmit(sendCodeHandler)}
          className={styles["login-input__form"]}
        >
          <div className={styles["login-input__fields"]}>
            <LoginField
              placeholder={t("login-placeholder")}
              disabled={
                sendCodeFromEmailMutation.isPending ||
                sendCodeFromPhoneMutation.isPending
              }
              isError={!!errors.login}
              errorMessage={t(errors.login?.message ?? "", { ns: "errors" })}
              onChange={onChangeFilled}
            />
          </div>
          <div className={styles["login-input__buttons"]}>
            <Button
              view="action"
              loading={
                sendCodeFromEmailMutation.isPending ||
                sendCodeFromPhoneMutation.isPending
              }
              type="submit"
              width="max"
            >
              {t("send-code-btn-title")}
            </Button>
            <Link
              href={ROUTES.login}
              disabled={
                sendCodeFromEmailMutation.isPending ||
                sendCodeFromPhoneMutation.isPending
              }
            >
              {t("return-to-login")}
            </Link>
          </div>
        </form>
      </WindowFrame>
    </div>
  );
}

export default LoginInput;
