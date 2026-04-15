import { useTranslation } from "react-i18next";

import { useEmailForm } from "@/features/userChangeEmail/models/forms";
import { WindowFrame, Input, Button } from "@/shared/ui";

import styles from "./EmailForm.module.scss";

function EmailForm({
  onCancel,
  onSuccess,
}: {
  onCancel: () => void;
  onSuccess: (email: string) => void;
}) {
  const { t } = useTranslation(["features.emailForm", "errors", "controls"]);
  const { emailField, errors, handleSubmit } = useEmailForm();
  const onSubmitHandler = handleSubmit(({ email }) => {
    onSuccess(email);
  });

  return (
    <WindowFrame title={t("title")}>
      <form className={styles["email-form"]} onSubmit={onSubmitHandler}>
        <Input
          placeholder={t("placeholder")}
          size="xl"
          autoFocus
          value={emailField.value}
          isError={!!errors.email}
          name={emailField.name}
          errorMessage={t(errors.email?.message ?? "", { ns: "errors" })}
          onChange={emailField.onChange}
          ref={emailField.ref}
        />
        <div className={styles["email-form__buttons"]}>
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

export default EmailForm;
