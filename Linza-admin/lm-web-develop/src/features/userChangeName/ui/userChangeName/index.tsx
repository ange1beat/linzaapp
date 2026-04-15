import { zodResolver } from "@hookform/resolvers/zod";
import { useController, useForm } from "react-hook-form";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router";

import { useUserQuery } from "@/entities/user";
import { useUserNameMutation } from "@/features/userChangeName/api/queries";
import { nameValidationSchema } from "@/features/userChangeName/models/validation";
import { ROUTES } from "@/shared/config";
import { WindowFrame, Input, Button, useAlert } from "@/shared/ui";

import styles from "./UserChangeName.module.scss";

interface IName {
  firstName: string;
  lastName: string;
}

function UserChangeNameFeature() {
  const { t } = useTranslation([
    "features.userChangeName",
    "errors",
    "controls",
  ]);

  const navigate = useNavigate();
  const { addAlert } = useAlert();
  const { user, isPending } = useUserQuery();
  const updateUserNameMutation = useUserNameMutation();

  const {
    handleSubmit,
    setError,
    clearErrors,
    formState: { errors },
    control,
  } = useForm<IName>({
    values: { firstName: user.firstName, lastName: user.lastName },
    resolver: zodResolver(nameValidationSchema),
  });

  const { field: firstName } = useController({
    control: control,
    name: "firstName",
  });
  const { field: lastName } = useController({
    control: control,
    name: "lastName",
  });

  const changeNameHandler = () => {
    clearErrors();
    updateUserNameMutation
      .mutateAsync({
        firstName: firstName.value,
        lastName: lastName.value,
      })
      .then(() => {
        navigate(ROUTES.profile);
        addAlert({
          title: t("success-title"),
          message: t("name-was-changed"),
          theme: "success",
        });
      })
      .catch((err) => {
        if (err.status === 400) {
          setError("firstName", {
            type: "custom",
            message: err.errors.firstName,
          });
          setError("lastName", {
            type: "custom",
            message: err.errors.lastName,
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

  const isLoading = updateUserNameMutation.isPending || isPending;

  return (
    <WindowFrame title={t("title")}>
      <form
        className={styles["change-name-form"]}
        onSubmit={handleSubmit(changeNameHandler)}
      >
        <div className={styles["change-name-form__inputs"]}>
          <Input
            value={firstName.value}
            ref={firstName.ref}
            onChange={firstName.onChange}
            isError={!!errors.firstName?.message}
            errorMessage={t(errors.firstName?.message ?? "", {
              ns: "errors",
            })}
            placeholder={t("placeholder-firstname")}
            size="xl"
            disabled={isLoading}
          />
          <Input
            value={lastName.value}
            ref={lastName.ref}
            onChange={lastName.onChange}
            isError={!!errors.lastName?.message}
            errorMessage={t(errors.lastName?.message ?? "", {
              ns: "errors",
            })}
            placeholder={t("placeholder-lastname")}
            size="xl"
            disabled={isLoading}
          />
        </div>
        <div className={styles["change-name-form__buttons"]}>
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
            onClick={() => navigate(ROUTES.profile)}
            loading={isLoading}
          >
            {t("cancel", { ns: "controls" })}
          </Button>
        </div>
      </form>
    </WindowFrame>
  );
}

export default UserChangeNameFeature;
