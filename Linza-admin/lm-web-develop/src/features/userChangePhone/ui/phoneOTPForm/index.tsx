import { useTranslation } from "react-i18next";

import { OTPForm } from "@/entities/auth";
import { useBackLng } from "@/entities/language";
import { env } from "@/shared/config";
import { useFirstRender } from "@/shared/hooks";
import { phoneNumberFormatter } from "@/shared/lib/phoneNumber";
import { WindowFrame, Input, Text, useAlert, Timer } from "@/shared/ui";

import { usePhoneMutation, usePhoneOTPMutation } from "../../api/queries";

import styles from "./PhoneOTPForm.module.scss";

function PhoneOTPForm({
  phone,
  onBack,
  onSuccess,
}: {
  phone: string;
  onBack: () => void;
  onSuccess: () => void;
}) {
  const { t } = useTranslation(["features.phoneOTPForm", "errors"]);
  const language = useBackLng();
  const { addAlert } = useAlert();
  const phoneMutation = usePhoneMutation();
  const phoneOTPMutation = usePhoneOTPMutation();

  const onSubmitHandler = (otpValue: string) => {
    return phoneMutation
      .mutateAsync({ otpValue, phone })
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

  const onRequestByPhone = () => {
    phoneOTPMutation.mutateAsync({ phoneNumber: phone, language }).catch(() => {
      addAlert({
        title: t("title", { ns: "errors" }),
        message: t("server-error", { ns: "errors" }),
        theme: "danger",
      });
    });
  };

  useFirstRender(onRequestByPhone);

  const isLoading = phoneMutation.isPending;
  return (
    <WindowFrame title={t("title")}>
      <div className={styles["phone-otp-form"]}>
        <Input
          size="xl"
          value={phoneNumberFormatter(phone).phone}
          disabled={true}
          isError={false}
          errorMessage={t("", { ns: "errors" })}
          onChange={() => {}}
        />
        <div className={styles["phone-otp-form__otp"]}>
          <Text className={styles["phone-otp-form__subtitle"]} variant="body-1">
            {t("sub-title")}
          </Text>
          <OTPForm
            isLoading={isLoading}
            phone={phone}
            onSubmit={onSubmitHandler}
            onBack={onBack}
          >
            <Timer
              isLoading={phoneOTPMutation.isPending}
              timer={env.RE_REQUEST_SECONDS}
              actions={onRequestByPhone}
              tabIndex={-1}
            />
          </OTPForm>
        </div>
      </div>
    </WindowFrame>
  );
}

export default PhoneOTPForm;
