import React from "react";

import { Trans, useTranslation } from "react-i18next";

import { PasswordRules } from "@/entities/auth";
import { ROUTES } from "@/shared/config";
import { flatErrors } from "@/shared/lib/errors";
import {
  Button,
  InputPassword,
  Link,
  useAlert,
  WindowFrame,
} from "@/shared/ui";

import { usePasswordMutation } from "../../api/queries";
import { useSetPasswordForm } from "../../models/forms";

import styles from "./SetPassword.module.scss";

function SetPassword({
  recoveryToken,
  onClick,
  onError,
  onSuccess,
  className,
}: {
  recoveryToken: string;
  onClick?: () => void;
  onSuccess: () => void;
  onError?: (errors: { [name: string]: string }) => void;
  className?: string;
}) {
  const { t } = useTranslation(["features.setPassword", "errors"]);
  const {
    passwordField,
    confirmPasswordField,
    errors,
    handleSubmit,
    setError,
    clearErrors,
    watch,
  } = useSetPasswordForm();
  const passwordMutation = usePasswordMutation();
  const { addAlert } = useAlert();

  const handleResetPassword = (pass: string) => {
    clearErrors();
    onClick?.();
    passwordMutation
      .mutateAsync({ recoveryToken, newPassword: pass })
      .then(onSuccess)
      .catch((err) => {
        if (err.status === 400) {
          setError("password", {
            type: "custom",
            message: flatErrors(err.errors).newPassword,
          });
        } else {
          addAlert({
            title: t("title", { ns: "errors" }),
            message: t("server-error", { ns: "errors" }),
            theme: "danger",
          });
        }
        onError?.(err);
      });
  };

  return (
    <div className={className}>
      <WindowFrame
        className={styles["set-password"]}
        title={<Trans i18nKey="title" t={t} />}
      >
        <form
          className={styles["set-password__form"]}
          onSubmit={handleSubmit((data) => handleResetPassword(data.password))}
          onChange={() => watch()}
        >
          <div className={styles["set-password__container"]}>
            <div className={styles["set-password__fields"]}>
              <InputPassword
                value={passwordField.value ?? ""}
                disabled={passwordField.disabled}
                isError={!!errors.password}
                errorMessage={t(errors.password?.message ?? "", {
                  ns: "errors",
                })}
                placeholder={t("password-placeholder")}
                onChange={passwordField.onChange}
                ref={passwordField.ref}
                autoFocus
              />

              <InputPassword
                value={confirmPasswordField.value ?? ""}
                disabled={confirmPasswordField.disabled}
                isError={!!errors.confirmPassword}
                errorMessage={t(errors.confirmPassword?.message ?? "", {
                  ns: "errors",
                })}
                placeholder={t("confirm-password-placeholder")}
                onChange={confirmPasswordField.onChange}
              />
            </div>
            <PasswordRules />
            <Button
              className={styles["set-password__reset-button"]}
              view="action"
              width="max"
              type="submit"
            >
              {t("reset-password")}
            </Button>
            <Link
              className={styles["set-password__back-link"]}
              href={ROUTES.login}
            >
              {t("back-to-login")}
            </Link>
          </div>
        </form>
      </WindowFrame>
    </div>
  );
}

export default SetPassword;
