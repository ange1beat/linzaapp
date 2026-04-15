import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router";

import { useUserQuery } from "@/entities/user";
import { ROUTES } from "@/shared/config";
import { WindowFrame, Input, Button, useAlert } from "@/shared/ui";

import { useTelegramMutation } from "../../api/queries";
import { useTelegramForm } from "../../models/forms";

import styles from "./UserChangeTelegram.module.scss";
import { getTelegram } from "@/features/userChangeTelegram/lib/getTelegram";

function UserChangeTelegram() {
  const { t } = useTranslation([
    "features.userChangeTelegram",
    "errors",
    "controls",
  ]);
  const { isPending, user } = useUserQuery();
  const { telegramField, handleSubmit, errors, setError } = useTelegramForm(
    user.telegramUsername ?? "",
  );
  const telegramMutation = useTelegramMutation();
  const { addAlert } = useAlert();
  const navigate = useNavigate();

  const submitHandler = handleSubmit(({ telegram }) => {
    telegramMutation
      .mutateAsync(telegram)
      .then(() => {
        navigate(ROUTES.profile);
        addAlert({
          title: t("success-update.title"),
          theme: "success",
          message: t("success-update.message"),
        });
      })
      .catch((response) => {
        if (response.status == 400) {
          setError("telegram", {
            type: "custom",
            message: response.errors.username,
          });
        } else {
          addAlert({
            title: t("title", { ns: "errors" }),
            message: t("server-error", { ns: "errors" }),
            theme: "danger",
          });
        }
      });
  });

  const onCancelHandler = () => {
    navigate(ROUTES.profile);
  };

  const isLoading = isPending || telegramMutation.isPending;
  return (
    <WindowFrame title={t("title")}>
      <form className={styles["user-change-telegram"]} onSubmit={submitHandler}>
        <Input
          placeholder={t("placeholder")}
          size="xl"
          autoFocus
          value={getTelegram(telegramField.value)}
          disabled={isLoading}
          isError={!!errors.telegram}
          errorMessage={t(errors.telegram?.message ?? "", { ns: "errors" })}
          onChange={telegramField.onChange}
          ref={telegramField.ref}
        />
        <div className={styles["user-change-telegram__buttons"]}>
          <Button
            view="action"
            size="xl"
            width="max"
            type="submit"
            loading={isLoading}
          >
            {t("confirm", { ns: "controls" })}
          </Button>
          <Button
            view="normal"
            size="xl"
            width="max"
            loading={isLoading}
            onClick={onCancelHandler}
          >
            {t("cancel", { ns: "controls" })}
          </Button>
        </div>
      </form>
    </WindowFrame>
  );
}

export default UserChangeTelegram;
