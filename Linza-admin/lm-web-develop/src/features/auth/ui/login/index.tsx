import React from "react";

import { zodResolver } from "@hookform/resolvers/zod";
import cn from "classnames";
import { useController, useForm } from "react-hook-form";
import { Trans, useTranslation } from "react-i18next";
import { z } from "zod";

import { LoginField, LoginType } from "@/entities/auth";
import { IUserLogin } from "@/entities/session";
import { httpDateToMinutes } from "@/features/auth/lib/formatTime";
import { loginSchema } from "@/features/auth/models/validation";
import { ROUTES } from "@/shared/config";
import { useAlert } from "@/shared/ui";
import Button from "@/shared/ui/button";
import InputPassword from "@/shared/ui/inputPassword";
import Link from "@/shared/ui/link";
import WindowFrame from "@/shared/ui/windowFrame";

import { useAuthorizeUser } from "../../api/queries";

import styles from "./LoginFeature.module.scss";

function LoginFeature({
  className,
  onSuccess,
  onError,
}: {
  className?: string;
  onSuccess: (user: IUserLogin, token: string, loginType: LoginType) => void;
  onError?: () => void;
}) {
  const { t } = useTranslation(["features.login", "errors"]);
  const { addAlert } = useAlert();
  const {
    handleSubmit,
    control,
    formState: { errors },
    setError,
    clearErrors,
  } = useForm<z.infer<typeof loginSchema>>({
    resolver: zodResolver(loginSchema),
  });

  const { field: loginField } = useController({
    control: control,
    name: "login",
  });
  const { field: passwordField } = useController({
    control: control,
    name: "password",
  });
  const { field: loginTypeField } = useController({
    control: control,
    name: "loginType",
  });
  const authorizeUserMutation = useAuthorizeUser();

  const onSubmit = handleSubmit(({ login, password, loginType }) => {
    clearErrors();
    return authorizeUserMutation
      .mutateAsync({ login, password })
      .then((res) => {
        onSuccess(res.user, res.stateToken, loginType);
      })
      .catch((err) => {
        onError?.();
        if (err.status === 500) {
          addAlert({
            title: t("error-title"),
            message: t("server-error"),
            theme: "danger",
          });
          return;
        }
        if (err.status === 401 && err.retryAfterValue) {
          const minutes = httpDateToMinutes(err.retryAfterValue);

          addAlert({
            title: t("error-title"),
            message: t("locked-user", { minutes: minutes }),
            theme: "danger",
          });
          return;
        } else {
          setError("login", {
            type: "custom",
            message: "login.wrong-data",
          });
          setError("password", {
            type: "custom",
            message: "password.wrong-data",
          });
        }
      });
  });
  const classes = cn(className, styles["login-widget"]);
  const isLoading = authorizeUserMutation.isPending;
  return (
    <div className={classes}>
      <WindowFrame
        className={styles["login-widget__form"]}
        title={<Trans i18nKey="title" t={t} />}
      >
        <form className={styles["login-widget__container"]} onSubmit={onSubmit}>
          <div className={styles["login-widget__fields"]}>
            <LoginField
              placeholder={t("login-placeholder")}
              disabled={isLoading}
              isError={!!errors.login}
              errorMessage={t(errors.login?.message || "", { ns: "errors" })}
              onChange={(v, type) => {
                loginField.onChange(v);
                loginTypeField.onChange(type);
              }}
            />
            <InputPassword
              value={passwordField.value}
              disabled={isLoading}
              isError={!!errors.password}
              errorMessage={t(errors.password?.message || "", { ns: "errors" })}
              placeholder={t("password-placeholder")}
              onChange={passwordField.onChange}
              ref={passwordField.ref}
            />
          </div>

          <div className={styles["login-widget__button"]}>
            <Button view="action" type="submit" loading={isLoading} width="max">
              {t("log-in-btn")}
            </Button>
          </div>

          <Link
            className={styles["login-widget__link"]}
            href={ROUTES.forgotPassword}
          >
            {t("forgot-password")}
          </Link>
        </form>
      </WindowFrame>
    </div>
  );
}

LoginFeature.prototype = {
  onSuccess: () => {},
  onError: () => {},
};

export default LoginFeature;
