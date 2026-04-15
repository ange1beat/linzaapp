import { useTranslation } from "react-i18next";

import { WindowFrame, Button, PhoneNumberField } from "@/shared/ui";

import { usePhoneForm } from "../../models/forms";

import styles from "./PhoneForm.module.scss";

function PhoneForm({
  onCancel,
  onSuccess,
}: {
  onCancel: () => void;
  onSuccess: (phone: string) => void;
}) {
  const { t } = useTranslation(["features.phoneForm", "errors", "controls"]);
  const { phoneField, isValidField, errors, handleSubmit } = usePhoneForm();
  const onSubmitHandler = handleSubmit(({ phone }) => {
    onSuccess(phone);
  });

  return (
    <WindowFrame title={t("title")}>
      <form className={styles["phone-form"]} onSubmit={onSubmitHandler}>
        <PhoneNumberField
          autoFocus={true}
          isError={!!errors.phone}
          errorMessage={t(errors.phone?.message ?? "", { ns: "errors" })}
          placeholder={t("placeholder")}
          onChange={(value) => {
            phoneField.onChange(value.phone);
            isValidField.onChange(value.isValid);
          }}
        />

        <div className={styles["phone-form__buttons"]}>
          <Button view="action" size="xl" width="max" type="submit">
            {t("send-code", { ns: "controls" })}
          </Button>
          <Button view="normal" size="xl" width="max" onClick={onCancel}>
            {t("cancel", { ns: "controls" })}
          </Button>
        </div>
      </form>
    </WindowFrame>
  );
}

export default PhoneForm;
