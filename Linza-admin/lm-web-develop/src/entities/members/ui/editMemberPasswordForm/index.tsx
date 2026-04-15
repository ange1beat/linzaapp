import React from "react";

import cn from "classnames";
import { SubmitHandler, useController, useForm } from "react-hook-form";
import { useTranslation } from "react-i18next";

import { defaultAva } from "@/entities/members";
import { useGetMemberQuery } from "@/entities/members/api/queries";
import {
  Button,
  InputPassword,
  ModalWindow,
  Skeleton,
  Text,
  Link,
} from "@/shared/ui";

import styles from "./EditMemberPasswordFormEntity.module.scss";

export interface IFormData {
  newPassword: string;
  confirmPassword: string;
}

interface IMemberPasswordFormEntityProps {
  className?: string;
  isLoad: boolean;
  errors: Partial<IFormData>;
  onSubmit: (data: IFormData, reset: () => void) => void;
  onChange: (data: IFormData) => void;
  onCancel: () => void;
  isOpen: boolean;
  memberId: string;
}

export function EditMemberPasswordFormEntity({
  isLoad,
  errors,
  onCancel,
  onSubmit,
  onChange,
  className,
  isOpen,
  memberId,
}: IMemberPasswordFormEntityProps) {
  const { t } = useTranslation("entities.editMemberPasswordForm");

  const { isPending, selectedMember } = useGetMemberQuery(memberId);

  const { handleSubmit, watch, control, reset } = useForm<IFormData>();
  const { field: newPassword } = useController({
    control: control,
    name: "newPassword",
  });
  const { field: confirmPassword } = useController({
    control: control,
    name: "confirmPassword",
  });
  const submit: SubmitHandler<IFormData> = (data) => {
    onSubmit(data, reset);
  };

  const onChangeHandler = () => {
    const value = watch();
    onChange(value);
  };

  const classes = cn(styles.member, className);
  return (
    <ModalWindow isOpen={isOpen} title={t("modal-title")} onClose={onCancel}>
      <div className={classes}>
        <div className={styles["member__user-info"]}>
          <div className={styles["member__image-wrapper"]}>
            <img
              src={selectedMember.avatarUrl || defaultAva}
              alt={t("image-alt")}
              className={styles["member__image-avatar"]}
            />
          </div>
          <div className={styles["member__full-name-and-contacts"]}>
            <Skeleton isLoad={isPending} height={24}>
              <Text variant="modal-name">
                {selectedMember.firstName + " " + selectedMember.lastName}
              </Text>
            </Skeleton>
            <Skeleton isLoad={isPending} height={16}>
              <Text variant="modal-email">{selectedMember.email}</Text>
            </Skeleton>
            <Skeleton isLoad={isPending} height={18}>
              <Link
                href={`https://t.me/${selectedMember.telegramUsername}`}
                target="_blank"
                className={styles["member__link"]}
              >
                @{selectedMember.telegramUsername}
              </Link>
            </Skeleton>
          </div>
        </div>
        <div className={styles["member__user-form-wrapper"]}>
          <Text variant="body-2">{t("form-title")}</Text>
          <form
            name="memberPasswordForm"
            onChange={onChangeHandler}
            onSubmit={handleSubmit(submit)}
            className={styles["member__user-form"]}
          >
            <InputPassword
              name="newPassword"
              placeholder={t("new-password-placeholder")}
              value={newPassword.value ?? ""}
              onChange={newPassword.onChange}
              ref={newPassword.ref}
              isError={!!errors.newPassword}
              disabled={isLoad}
              errorMessage={errors.newPassword}
            />
            <InputPassword
              name="confirmPassword"
              placeholder={t("confirm-password-placeholder")}
              value={confirmPassword.value ?? ""}
              onChange={confirmPassword.onChange}
              ref={confirmPassword.ref}
              isError={!!errors.confirmPassword}
              disabled={isLoad}
              errorMessage={errors.confirmPassword}
            />
            <div className={styles["member__user-form__buttons"]}>
              <Button
                view="normal"
                size="l"
                loading={isLoad}
                onClick={onCancel}
              >
                {t("buttons.cancel")}
              </Button>
              <Button view="action" size="l" type="submit" disabled={isLoad}>
                {t("buttons.apply")}
              </Button>
            </div>
          </form>
        </div>
      </div>
    </ModalWindow>
  );
}
