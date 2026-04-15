import { useState } from "react";

import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router";

import { ROUTES } from "@/shared/config";
import { useAlert } from "@/shared/ui";

import EmailForm from "../emailForm";
import EmailOTPForm from "../emailOTPForm";

function ChangeEmail() {
  const { t } = useTranslation("features.changeEmail");
  const navigate = useNavigate();
  const [step, setStep] = useState<1 | 2>(1);
  const [email, setEmail] = useState<string>("");
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

  const onNextHandler = (formEmail: string) => {
    setEmail(formEmail);
    setStep(2);
  };

  return (
    <>
      {step === 1 && (
        <EmailForm onSuccess={onNextHandler} onCancel={onCancelHandler} />
      )}
      {step === 2 && (
        <EmailOTPForm
          onSuccess={onSuccessHandler}
          onBack={onBackHandler}
          email={email}
        />
      )}
    </>
  );
}

export default ChangeEmail;
