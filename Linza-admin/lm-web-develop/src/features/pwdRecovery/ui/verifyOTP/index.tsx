import { ReactNode, useState } from "react";

import { useTranslation } from "react-i18next";

import { ConfirmCodeForResetPassword, LoginType } from "@/entities/auth";
import { useAlert, KEY_FIELD_LENGTH } from "@/shared/ui";

import { useRecoveryVerifyMutation } from "../../api/queries";

function VerifyOTP({
  children,
  onClick,
  onSuccess,
  onError,
  className,
  login,
  loginType,
  onBack,
}: {
  children: ReactNode;
  onClick?: () => void;
  onSuccess: (recoveryToken: string) => void;
  onError?: () => void;
  className?: string;
  login: string;
  loginType: LoginType;
  onBack: () => void;
}) {
  const { t } = useTranslation(["features.verifyOTP", "errors"]);
  const [errorOtpCode, setErrorOtpCode] = useState("");
  const sendOtpCodeMutation = useRecoveryVerifyMutation();
  const { addAlert } = useAlert();

  const onSubmitConfirmCodeHandler = (recoveryCode: string) => {
    if (recoveryCode.length !== KEY_FIELD_LENGTH) {
      setErrorOtpCode("error-incorrect");
      return;
    }
    onClick && onClick();
    sendOtpCodeMutation
      .mutateAsync({ login, recoveryCode })
      .then((res) => onSuccess(res.recoveryToken))
      .catch((e) => {
        onError?.();
        if (e.status === 401 || e.status === 403) {
          setErrorOtpCode("error-incorrect");
        } else {
          addAlert({
            title: t("title", { ns: "errors" }),
            message: t("server-error", { ns: "errors" }),
            theme: "danger",
          });
        }
      });
  };

  return (
    <div className={className}>
      <ConfirmCodeForResetPassword
        error={t(errorOtpCode)}
        onSubmit={onSubmitConfirmCodeHandler}
        onBack={onBack}
        loginType={loginType}
        loading={sendOtpCodeMutation.isPending}
      >
        {children}
      </ConfirmCodeForResetPassword>
    </div>
  );
}

export default VerifyOTP;
