import React from "react";

import cn from "classnames";
import { useTranslation } from "react-i18next";

import { LoginType } from "@/entities/auth";
import { useBackLng } from "@/entities/language";
import { env } from "@/shared/config";
import { Text, Timer } from "@/shared/ui";

import { useRecoveryPDWBySMS, useRecoveryPDWByEmail } from "../../api/queries";

import styles from "./OTPReRequest.module.scss";

function OTPReRequest({
  clasName,
  timer,
  login,
  loginType,
  onSuccess,
  onError,
}: {
  clasName?: string;
  timer: number;
  login: string;
  loginType: LoginType;
  onSuccess?: () => void;
  onError?: () => void;
}) {
  const { t } = useTranslation("features.otpReRequest");
  const sendOtpByEmailMutation = useRecoveryPDWByEmail();
  const sendOtpBySMSMutation = useRecoveryPDWBySMS();
  const locale = useBackLng();

  const onClickHandler = () => {
    if (loginType === "email") {
      sendOtpBySMSMutation.reset();
      sendOtpByEmailMutation
        .mutateAsync({ email: login, locale })
        .then(onSuccess)
        .catch(onError);
    }

    if (loginType === "phone") {
      sendOtpByEmailMutation.reset();
      sendOtpBySMSMutation
        .mutateAsync({ phoneNumber: login, locale })
        .then(onSuccess)
        .catch(onError);
    }
  };

  const isLoading =
    sendOtpByEmailMutation.isPending || sendOtpBySMSMutation.isPending;
  const isError =
    sendOtpByEmailMutation.isError || sendOtpBySMSMutation.isError;
  const classes = cn(clasName, styles["otp-re-request"]);
  return (
    <div className={classes}>
      <Timer
        timer={timer}
        template={(time) => t("request-wait", { timer: time })}
        countDownEndText={t("request-again")}
        isLoading={isLoading}
        actions={onClickHandler}
      />
      {isError && (
        <Text variant="body-2" className={styles["otp-re-request__error"]}>
          {t("error")}
        </Text>
      )}
    </div>
  );
}

OTPReRequest.defaultProps = {
  timer: env.RE_REQUEST_SECONDS,
  onSuccess: () => null,
  onError: () => null,
};

export default OTPReRequest;
