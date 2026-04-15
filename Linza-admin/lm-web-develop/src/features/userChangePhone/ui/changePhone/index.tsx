import { useState } from "react";

import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router";

import PhoneForm from "@/features/userChangePhone/ui/phoneForm";
import { ROUTES } from "@/shared/config";
import { useAlert } from "@/shared/ui";

import PhoneOTPForm from "../phoneOTPForm";

function ChangePhone() {
  const { t } = useTranslation("features.ChangePhone");
  const navigate = useNavigate();
  const [step, setStep] = useState<1 | 2>(1);
  const [phone, setPhone] = useState<string>("");
  const { addAlert } = useAlert();

  const onCancelHandler = () => {
    navigate(ROUTES.profile);
  };

  const onSuccessHandler = () => {
    navigate(ROUTES.profile);
    addAlert({
      title: t("success-update.title"),
      message: t("success-update.message"),
      theme: "success",
    });
  };

  const onBackHandler = () => {
    setStep(1);
  };

  const onNextHandler = (formPhone: string) => {
    setPhone(formPhone);
    setStep(2);
  };

  return (
    <>
      {step === 1 && (
        <PhoneForm onSuccess={onNextHandler} onCancel={onCancelHandler} />
      )}
      {step === 2 && (
        <PhoneOTPForm
          onSuccess={onSuccessHandler}
          onBack={onBackHandler}
          phone={phone}
        />
      )}
    </>
  );
}

export default ChangePhone;
