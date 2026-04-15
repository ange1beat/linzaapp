import React from "react";

import { Envelope } from "@gravity-ui/icons";
import cn from "classnames";
import { useTranslation } from "react-i18next";

import { useBackLng } from "@/entities/language";
import { flatErrors } from "@/shared/lib";
import { Button, Input, ModalWindow, useAlert } from "@/shared/ui";

import { useCreateMember } from "../../api/queries";
import { useMemberAddForm } from "../../models/forms";

import styles from "./MemberAdd.module.scss";

interface IMemberForm {
  children: React.ReactNode;
  onSuccess?: () => void;
  onCancel?: () => void;
  className?: string;
}
interface IMemberData {
  email: string;
}
function MemberAdd({ onSuccess, onCancel, className, children }: IMemberForm) {
  const { t } = useTranslation(["features.memberAdd", "errors", "controls"]);
  const [modalOpen, setModalOpen] = React.useState<boolean>(false);
  const createMemberMutation = useCreateMember();
  const { addAlert } = useAlert();
  const language = useBackLng();

  const { errors, emailField, setError, handleSubmit, reset } =
    useMemberAddForm("");

  const addMemberHandler = (value: IMemberData) => {
    createMemberMutation
      .mutateAsync({ email: value.email, language })
      .then(() => {
        addAlert({
          title: t("title-success"),
          message: t("message-success"),
          theme: "success",
        });
        setModalOpen(false);
        onSuccess?.();
        reset();
      })
      .catch((response) => {
        if (response.status === 400) {
          setError("email", {
            type: "custom",
            message: flatErrors(response.errors).email,
          });
        } else if (response.status === 409) {
          setError("email", {
            type: "custom",
            message: "email.already-used",
          });
        } else {
          addAlert({
            title: t("title", { ns: "errors" }),
            message: t("server-error", { ns: "errors" }),
            theme: "danger",
          });
          setModalOpen(false);
          onCancel?.();
          reset();
        }
      });
  };

  const onCancelHandler = () => {
    reset();
    setModalOpen(!modalOpen);
    onCancel?.();
  };

  const classes = cn(styles["member-form"], className);
  const isLoad = createMemberMutation.isPending;

  return (
    <>
      <div onClick={() => setModalOpen(!modalOpen)}>{children}</div>
      <ModalWindow
        title={t("title")}
        isOpen={modalOpen}
        onClose={onCancelHandler}
      >
        <div className={classes}>
          <form
            className={styles["member-form__form"]}
            onSubmit={handleSubmit(addMemberHandler)}
          >
            <div className={styles["member-form__fields"]}>
              <Input
                ref={emailField.ref}
                value={emailField.value}
                disabled={isLoad}
                rightContent={<Envelope className={styles["input__icon"]} />}
                isError={!!errors?.email?.message}
                errorMessage={t(errors.email?.message ?? "", { ns: "errors" })}
                placeholder={t("email")}
                onChange={emailField.onChange}
                autoFocus
              />
            </div>

            <div className={styles["member-form__buttons"]}>
              <Button
                onClick={onCancelHandler}
                view="normal"
                size="l"
                loading={isLoad}
              >
                {t("cancel", { ns: "controls" })}
              </Button>
              <Button view="action" size="l" loading={isLoad} type="submit">
                {t("confirm", { ns: "controls" })}
              </Button>
            </div>
          </form>
        </div>
      </ModalWindow>
    </>
  );
}

export default MemberAdd;
