import React from "react";

import { LogoTelegram, Envelope, Smartphone } from "@gravity-ui/icons";
import cn from "classnames";
import { useController, useForm } from "react-hook-form";
import { useTranslation } from "react-i18next";

import { defaultAva } from "@/entities/members";
import { Button, Input, ModalWindow, Text } from "@/shared/ui/";

import styles from "./EditMember.module.scss";

interface IEditMember {
  className?: string;
  isOpen: boolean;
  isLoad: boolean;
  isDisabled: boolean;
  data: IMemberData;
  errors: IMemberErrors;
  onSubmit: (data: IMemberData) => void;
  onCancel: () => void;
  onChange: (data: IMemberData) => void;
}

interface IMemberData {
  id: string;
  firstName: string;
  lastName: string;
  email: string;
  phoneNumber: string;
  telegramUsername?: string;
  avatarUrl?: string;
}

interface IMemberErrors {
  firstName?: string;
  lastName?: string;
  email?: string;
  phoneNumber?: string;
  telegramUsername?: string;
}
function EditMember({
  className,
  isLoad,
  isOpen,
  isDisabled,
  errors,
  data,
  onChange,
  onSubmit,
  onCancel,
}: IEditMember) {
  const { t } = useTranslation("entities.editMember");
  const classes = cn(styles["edit-member"], className);
  const { handleSubmit, control, watch } = useForm({
    values: {
      id: data.id || "",
      avatarUrl: data.avatarUrl || "",
      firstName: data.firstName || "",
      lastName: data.lastName || "",
      phoneNumber: data.phoneNumber || "",
      email: data.email || "",
      telegramUsername: data.telegramUsername || "",
    },
  });
  const onChangeHandler = () => {
    const value = watch();
    onChange(value);
  };

  const { field: firstName } = useController({
    control: control,
    name: "firstName",
  });
  const { field: lastName } = useController({
    control: control,
    name: "lastName",
  });
  const { field: phoneNumber } = useController({
    control: control,
    name: "phoneNumber",
  });
  const { field: email } = useController({
    control: control,
    name: "email",
  });
  const { field: telegramUsername } = useController({
    control: control,
    name: "telegramUsername",
  });

  return (
    <ModalWindow isOpen={isOpen} title={t("title")} onClose={onCancel}>
      <div className={classes}>
        <form
          className={styles["main-info__form"]}
          onChange={onChangeHandler}
          onSubmit={handleSubmit(onSubmit)}
        >
          <div className={styles["edit-member__main-info"]}>
            <div>
              <img
                className={styles["main-info__avatar"]}
                src={data.avatarUrl || defaultAva}
                alt="avatar"
              />
            </div>
            <div className={styles["main-info__field"]}>
              <Input
                name="firstName"
                ref={firstName.ref}
                value={firstName.value}
                disabled={isLoad}
                isError={!!errors?.firstName}
                errorMessage={errors?.firstName}
                placeholder={t("first-name-placeholder")}
                onChange={firstName.onChange}
              />
              <Input
                name="lastName"
                ref={lastName.ref}
                value={lastName.value}
                disabled={isLoad}
                isError={!!errors?.lastName}
                errorMessage={errors?.lastName}
                placeholder={t("last-name-placeholder")}
                onChange={lastName.onChange}
              />
              <Input
                name="telegramUsername"
                ref={telegramUsername.ref}
                value={telegramUsername.value}
                disabled={isLoad}
                rightContent={<LogoTelegram />}
                isError={!!errors?.telegramUsername}
                errorMessage={errors?.telegramUsername}
                placeholder={t("telegram-placeholder")}
                onChange={telegramUsername.onChange}
              />
            </div>
          </div>

          <div className={styles["edit-member__auth-info"]}>
            <Text variant={"body-2"}>{t("auth-title")}</Text>
            <Input
              name="email"
              ref={email.ref}
              value={email.value}
              disabled={isLoad}
              rightContent={<Envelope />}
              isError={!!errors?.email}
              errorMessage={errors?.email}
              placeholder={t("email-placeholder")}
              onChange={email.onChange}
            />
            <Input
              name="phoneNumber"
              ref={phoneNumber.ref}
              value={phoneNumber.value}
              disabled={isLoad}
              rightContent={<Smartphone />}
              isError={!!errors?.phoneNumber}
              errorMessage={errors?.phoneNumber}
              placeholder={t("phone-placeholder")}
              onChange={phoneNumber.onChange}
            />
            <div className={styles["edit-member__buttons"]}>
              <Button
                onClick={onCancel}
                className={styles["registration-form__button"]}
                view="normal"
                loading={isLoad}
                type="button"
              >
                {t("button-cancel")}
              </Button>
              <Button
                onClick={() => {}}
                className={styles["registration-form__button"]}
                view="action"
                loading={isLoad}
                type="submit"
                disabled={isDisabled}
              >
                {t("button-apply")}
              </Button>
            </div>
          </div>
        </form>
      </div>
    </ModalWindow>
  );
}

export default EditMember;
