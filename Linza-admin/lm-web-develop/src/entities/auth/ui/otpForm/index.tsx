import { ReactNode } from "react";

import cn from "classnames";
import { useTranslation } from "react-i18next";

import { Button, KeyField } from "@/shared/ui";

import { useOTPForm } from "../../models/forms";

import styles from "./OTPForm.module.scss";

function OTPForm({
  className,
  children,
  isLoading,
  onSubmit,
  onBack,
}: {
  className?: string;
  isLoading: boolean;
  email?: string;
  phone?: string;
  children: ReactNode;
  onSubmit: (otpValue: string) => Promise<void>;
  onBack: () => void;
}) {
  const { t } = useTranslation(["errors", "controls"]);
  const { otpField, handleSubmit, errors, setError } = useOTPForm();

  const onSubmitHandler = handleSubmit(({ otp }) => {
    onSubmit(otp).catch(() => {
      setError("otp", {
        type: "custom",
        message: "otp.incorrect",
      });
    });
  });

  const classes = cn(styles["otp-form"], className);
  return (
    <form className={classes} onSubmit={onSubmitHandler}>
      <div>
        <KeyField
          className={styles["otp-form__code"]}
          disabled={isLoading}
          isError={!!errors.otp?.message}
          errorMessage={t(errors.otp?.message ?? "", { ns: "errors" })}
          onChange={otpField.onChange}
        />
        {children}
      </div>
      <div className={styles["otp-form__buttons"]}>
        <Button type="submit" view="action" loading={isLoading}>
          {t("confirm", { ns: "controls" })}
        </Button>
        <Button view="normal" loading={isLoading} onClick={onBack}>
          {t("back", { ns: "controls" })}
        </Button>
      </div>
    </form>
  );
}

export default OTPForm;
