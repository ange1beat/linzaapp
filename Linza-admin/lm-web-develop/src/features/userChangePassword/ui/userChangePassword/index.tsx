import { zodResolver } from "@hookform/resolvers/zod";
import { useController, useForm } from "react-hook-form";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router";

import PasswordRules from "@/entities/auth/ui/passwordRules";
import { useChangePasswordMutation } from "@/features/userChangePassword/api/queries";
import { updatePasswordSchema } from "@/features/userChangePassword/models/validation";
import { ROUTES } from "@/shared/config";
import { Button, InputPassword, useAlert, WindowFrame } from "@/shared/ui";

import styles from "./UserChangePassword.module.scss";

interface IForm {
  currentPassword: string;
  password: string;
  confirmPassword: string;
}

function UserChangePassword() {
  const { t } = useTranslation([
    "features.userChangePassword",
    "errors",
    "controls",
  ]);
  const navigate = useNavigate();
  const { addAlert } = useAlert();
  const {
    handleSubmit,
    setError,
    clearErrors,
    formState: { errors },
    control,
  } = useForm<IForm>({
    defaultValues: {
      currentPassword: "",
      password: "",
      confirmPassword: "",
    },
    resolver: zodResolver(updatePasswordSchema),
  });
  const updateUserNameMutation = useChangePasswordMutation();
  const { field: currentPassword } = useController({
    control: control,
    name: "currentPassword",
  });
  const { field: password } = useController({
    control: control,
    name: "password",
  });
  const { field: confirmPassword } = useController({
    control: control,
    name: "confirmPassword",
  });

  const changePasswordHandler = () => {
    clearErrors();
    updateUserNameMutation
      .mutateAsync({
        currentPassword: currentPassword.value,
        newPassword: password.value,
      })
      .then(() => {
        navigate(ROUTES.profile);
        addAlert({
          title: t("success-title"),
          message: t("message"),
          theme: "success",
        });
      })
      .catch((err) => {
        if (err.status === 400) {
          setError("currentPassword", {
            type: "custom",
            message: err.errors.currentPassword,
          });
          setError("password", {
            type: "custom",
            message: err.errors.password,
          });
        } else {
          addAlert({
            title: t("title", { ns: "errors" }),
            message: t("server-error", { ns: "errors" }),
            theme: "danger",
          });
        }
      });
  };

  return (
    <WindowFrame title={t("title")}>
      <form
        className={styles["password-change-form"]}
        onSubmit={handleSubmit(changePasswordHandler)}
      >
        <div className={styles["password-change-form__inputs"]}>
          <InputPassword
            value={currentPassword.value}
            ref={currentPassword.ref}
            onChange={currentPassword.onChange}
            isError={!!errors.currentPassword?.message}
            errorMessage={t(errors.currentPassword?.message ?? "", {
              ns: "errors",
            })}
            placeholder={t("current-password-placeholder")}
            size="xl"
            disabled={updateUserNameMutation.isPending}
          />
          <InputPassword
            value={password.value}
            ref={password.ref}
            onChange={password.onChange}
            isError={!!errors.password?.message}
            errorMessage={t(errors.password?.message ?? "", {
              ns: "errors",
            })}
            placeholder={t("new-password-placeholder")}
            size="xl"
            disabled={updateUserNameMutation.isPending}
          />
          <InputPassword
            value={confirmPassword.value}
            ref={confirmPassword.ref}
            onChange={confirmPassword.onChange}
            isError={!!errors.confirmPassword}
            errorMessage={t(errors.confirmPassword?.message ?? "", {
              ns: "errors",
            })}
            placeholder={t("confirm-password-placeholder")}
            size="xl"
            disabled={updateUserNameMutation.isPending}
          />
          <PasswordRules />
        </div>

        <div className={styles["password-change-form__buttons"]}>
          <Button
            view="action"
            size="xl"
            width="max"
            type="submit"
            loading={updateUserNameMutation.isPending}
          >
            {t("confirm", { ns: "controls" })}
          </Button>
          <Button
            view="normal"
            size="xl"
            width="max"
            onClick={() => navigate(ROUTES.profile)}
            loading={updateUserNameMutation.isPending}
          >
            {t("cancel", { ns: "controls" })}
          </Button>
        </div>
      </form>
    </WindowFrame>
  );
}

export default UserChangePassword;
