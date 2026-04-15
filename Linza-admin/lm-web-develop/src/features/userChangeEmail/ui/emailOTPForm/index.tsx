import { useTranslation } from "react-i18next";

import { OTPForm } from "@/entities/auth";
import { useBackLng } from "@/entities/language";
import { env } from "@/shared/config";
import { useFirstRender } from "@/shared/hooks";
import { WindowFrame, Input, Text, useAlert, Timer } from "@/shared/ui";

import { useEmailOTPMutation, useEmailMutation } from "../../api/queries";

import styles from "./EmailOTPForm.module.scss";

function EmailOTPForm({
  email,
  onBack,
  onSuccess,
}: {
  email: string;
  onBack: () => void;
  onSuccess: () => void;
}) {
  const { t } = useTranslation(["features.emailOTPForm", "errors"]);
  const language = useBackLng();
  const { addAlert } = useAlert();
  const emailMutation = useEmailMutation();
  const emailOTPMutation = useEmailOTPMutation();

  const onSubmitHandler = (otpValue: string) => {
    return emailMutation
      .mutateAsync({ otpValue, email })
      .then(onSuccess)
      .catch(async (error) => {
        const status = error.response.status;
        if (status === 400) {
          return Promise.reject();
        } else {
          addAlert({
            title: t("title", { ns: "errors" }),
            message: t("server-error", { ns: "errors" }),
            theme: "danger",
          });
        }
      });
  };

  const onRequestByEmail = () => {
    emailOTPMutation.mutateAsync({ email, language }).catch(() => {
      addAlert({
        title: t("title", { ns: "errors" }),
        message: t("server-error", { ns: "errors" }),
        theme: "danger",
      });
    });
  };

  useFirstRender(onRequestByEmail);

  const isLoading = emailMutation.isPending;
  return (
    <WindowFrame title={t("title")}>
      <div className={styles["email-otp-form"]}>
        <Input
          size="xl"
          value={email}
          disabled={true}
          isError={false}
          errorMessage={t("", { ns: "errors" })}
          onChange={() => {}}
        />
        <div className={styles["email-otp-form__otp"]}>
          <Text className={styles["email-otp-form__subtitle"]} variant="body-1">
            {t("sub-title")}
          </Text>
          <OTPForm
            isLoading={isLoading}
            email={email}
            onSubmit={onSubmitHandler}
            onBack={onBack}
          >
            <Timer
              isLoading={emailOTPMutation.isPending}
              timer={env.RE_REQUEST_SECONDS}
              actions={onRequestByEmail}
              tabIndex={-1}
            />
          </OTPForm>
        </div>
      </div>
    </WindowFrame>
  );
}

export default EmailOTPForm;
