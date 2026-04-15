import React from "react";

import cn from "classnames";
import { useTranslation } from "react-i18next";

import { LoginType, useSendOtpByEmail, useSendOtpBySMS } from "@/entities/auth";
import { useBackLng } from "@/entities/language";
import { env } from "@/shared/config";
import { Text, Timer } from "@/shared/ui";

import styles from "./CodeReRequest.module.scss";

function CodeReRequest({
  clasName,
  timer,
  loginType,
  stateToken,
  onSuccess,
  onError,
}: {
  clasName?: string;
  timer: number;
  stateToken: string;
  loginType: LoginType;
  onSuccess?: () => void;
  onError: () => void;
}) {
  const { t } = useTranslation("features.codeReRequest");
  const sendOtpByEmailMutation = useSendOtpByEmail();
  const sendOtpBySMSMutation = useSendOtpBySMS();
  const locale = useBackLng();

  const onClickHandler = () => {
    if (loginType === "email") {
      sendOtpBySMSMutation.reset();
      sendOtpByEmailMutation
        .mutateAsync({ stateToken, locale })
        .then(onSuccess)
        .catch(onError);
    }

    if (loginType === "phone") {
      sendOtpByEmailMutation.reset();
      sendOtpBySMSMutation
        .mutateAsync({ stateToken, locale })
        .then(onSuccess)
        .catch(onError);
    }
  };

  const isLoading =
    sendOtpByEmailMutation.isPending || sendOtpBySMSMutation.isPending;
  const isError =
    sendOtpByEmailMutation.isError || sendOtpBySMSMutation.isError;
  const classes = cn(clasName, styles["code-re-request"]);
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
        <Text variant="body-2" className={styles["code-re-request__error"]}>
          {t("error")}
        </Text>
      )}
    </div>
  );
}

CodeReRequest.defaultProps = {
  timer: env.RE_REQUEST_SECONDS,
  onSuccess: () => null,
  onError: () => null,
};

export default CodeReRequest;
