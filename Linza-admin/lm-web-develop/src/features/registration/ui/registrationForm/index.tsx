import React from "react";

import { zodResolver } from "@hookform/resolvers/zod";
import classNames from "classnames";
import { useController, useForm } from "react-hook-form";
import { Trans, useTranslation } from "react-i18next";

import PasswordRules from "@/entities/auth/ui/passwordRules";
import {
  Button,
  Input,
  InputPassword,
  useAlert,
  WindowFrame,
} from "@/shared/ui";

import { useCreateAccountMutation } from "../../api/queries";
import { createAccountSchema } from "../../models/validation";

import styles from "./RegistrationForm.module.scss";

function RegistrationForm({
  onSuccess,
  invitationId,
  className,
}: {
  className?: string;
  invitationId: string;
  onSuccess: () => void;
}) {
  const { t } = useTranslation("features.registrationForm");
  const { t: tErr } = useTranslation("errors");
  const createAccountMutation = useCreateAccountMutation();
  const classes = classNames(styles["confirmation-form"], className);

  const {
    handleSubmit,
    control,
    setError,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(createAccountSchema),
    defaultValues: {
      firstName: "",
      lastName: "",
      password: "",
      passwordConfirmation: "",
    },
  });

  const { field: firstName } = useController({
    control: control,
    name: "firstName",
  });
  const { field: lastName } = useController({
    control: control,
    name: "lastName",
  });
  const { field: password } = useController({
    control: control,
    name: "password",
  });
  const { field: passwordConfirmation } = useController({
    control: control,
    name: "passwordConfirmation",
  });

  const { addAlert } = useAlert();

  const onSubmitHandler = handleSubmit((data) => {
    createAccountMutation
      .mutateAsync({
        invitationId: invitationId,
        firstName: data.firstName,
        lastName: data.lastName,
        password: data.password,
      })
      .then(onSuccess)
      .catch(async (response) => {
        if (response.status === 400) {
          setError("firstName", {
            type: "custom",
            message: response.errors.errors.firstName,
          });
          setError("lastName", {
            type: "custom",
            message: response.errors.errors.lastName,
          });
          setError("password", {
            type: "custom",
            message: response.errors.errors.password,
          });
        }
        if (response.status === 403) {
          addAlert({
            title: tErr("title"),
            message: tErr("forbidden-error"),
            theme: "danger",
          });
        } else {
          addAlert({
            title: tErr("title"),
            message: tErr("server-error"),
            theme: "danger",
          });
        }
      });
  });

  const isLoad = createAccountMutation.isPending;
  return (
    <div className={classes}>
      <WindowFrame
        className={styles["registration-form"]}
        title={<Trans i18nKey="title" t={t} />}
      >
        <form
          className={styles["registration-form__main"]}
          onSubmit={onSubmitHandler}
          name="LoginForm"
        >
          <Input
            name="firstName"
            ref={firstName.ref}
            value={firstName.value ?? ""}
            disabled={isLoad}
            isError={!!errors?.firstName}
            errorMessage={tErr(errors?.firstName?.message ?? "")}
            placeholder={t("first-name-placeholder")}
            onChange={firstName.onChange}
            autoFocus={true}
          />
          <Input
            name="lastName"
            ref={lastName.ref}
            value={lastName.value ?? ""}
            disabled={isLoad}
            isError={!!errors?.lastName}
            errorMessage={tErr(errors?.lastName?.message ?? "")}
            placeholder={t("last-name-placeholder")}
            onChange={lastName.onChange}
          />
          <InputPassword
            name="password"
            ref={password.ref}
            value={password.value ?? ""}
            disabled={isLoad}
            isError={!!errors?.password}
            errorMessage={tErr(errors?.password?.message ?? "")}
            placeholder={t("password-placeholder")}
            onChange={password.onChange}
          />
          <InputPassword
            name="passwordConfirmation"
            ref={passwordConfirmation.ref}
            value={passwordConfirmation.value ?? ""}
            disabled={isLoad}
            isError={!!errors?.passwordConfirmation}
            errorMessage={tErr(errors?.passwordConfirmation?.message ?? "")}
            placeholder={t("password-confirm-placeholder")}
            onChange={passwordConfirmation.onChange}
          />
          <PasswordRules />
          <Button
            onClick={() => {}}
            className={styles["registration-form__button"]}
            view="action"
            loading={isLoad}
            type="submit"
          >
            {t("button")}
          </Button>
        </form>
      </WindowFrame>
    </div>
  );
}
export default RegistrationForm;
