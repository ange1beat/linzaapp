import React from "react";

import cn from "classnames";
import { useTranslation, Trans } from "react-i18next";

import { useSendOtpByEmail, useSendOtpBySMS, LoginType } from "@/entities/auth";
import { useBackLng } from "@/entities/language";
import { IUserLogin } from "@/entities/session";
import { useFirstRender } from "@/shared/hooks";

import CodeReRequest from "../../features/auth/ui/codeReRequest";
import ConfirmationForm from "../../features/auth/ui/confirmationForm";
import Button from "../../shared/ui/button";
import Text from "../../shared/ui/text";
import WindowFrame from "../../shared/ui/windowFrame";

import styles from "./AuthTwoFA.module.scss";

interface IAuthTwoFA {
  className?: string;
  isLoading: boolean;
  loginType: LoginType;
  stateToken: string;
  onSuccess: (user: IUserLogin, stateToken: string) => void;
  onError: () => void;
  onBack: () => void;
}
function AuthTwoFA({
  className,
  isLoading,
  loginType,
  stateToken,
  onBack,
  onError,
  onSuccess,
}: IAuthTwoFA) {
  const { t } = useTranslation("widgets.authTwoFA");
  const sendOtpByEmailMutation = useSendOtpByEmail();
  const sendOtpBySMSMutation = useSendOtpBySMS();
  const locale = useBackLng();

  useFirstRender(() => {
    if (loginType === "email") {
      sendOtpByEmailMutation.mutateAsync({ stateToken, locale }).catch(onError);
    } else {
      sendOtpBySMSMutation.mutateAsync({ stateToken, locale }).catch(onError);
    }
  });

  const classes = cn(styles["auth-two-fa"], className);

  return (
    <WindowFrame className={classes} title={<Trans i18nKey="title" t={t} />}>
      <div className={styles["auth-two-fa__container"]}>
        <Text variant="body-3">
          <Trans
            i18nKey={
              loginType === "email"
                ? "info-message-email"
                : "info-message-phone"
            }
            t={t}
          />
        </Text>

        <ConfirmationForm
          className={styles["auth-two-fa__input"]}
          isLoading={isLoading}
          stateToken={stateToken}
          onSuccess={onSuccess}
          onError={onError}
        >
          <CodeReRequest
            stateToken={stateToken}
            loginType={loginType}
            onError={onError}
          />
        </ConfirmationForm>
        <Button onClick={onBack} view="normal">
          {t("button-back")}
        </Button>
      </div>
    </WindowFrame>
  );
}
export default AuthTwoFA;
