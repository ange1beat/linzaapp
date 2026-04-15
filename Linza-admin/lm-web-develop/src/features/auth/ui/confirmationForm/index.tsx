import React, { useState } from "react";

import classNames from "classnames";
import { useTranslation } from "react-i18next";

import { IUserLogin } from "@/entities/session";
import { Button, KEY_FIELD_LENGTH, KeyField, useAlert } from "@/shared/ui";

import { useConfirmCode } from "../../api/queries";

import styles from "./ConfirmationForm.module.scss";

interface IConfirmationData {
  className?: string;
  isLoading: boolean;
  stateToken: string;
  onSuccess: (user: IUserLogin, stateToken: string) => void;
  onError: () => void;
  children: React.ReactNode;
}

function ConfirmationForm({
  className,
  isLoading,
  stateToken,
  children,
  onSuccess,
}: IConfirmationData) {
  const { t } = useTranslation("features.confirmationForm");
  const { t: tErr } = useTranslation("errors");
  const formClasses = classNames(styles["confirmation-form"], className);
  const [passcode, setPasscode] = useState("");
  const [isErrorChange, setIsErrorChange] = useState(false);
  const sendConfirmCodeMutation = useConfirmCode();
  const { addAlert } = useAlert();
  const onSendConfirmCode = () => {
    if (passcode.length === KEY_FIELD_LENGTH) {
      sendConfirmCodeMutation
        .mutateAsync({
          stateToken,
          passcode,
        })
        .then((value) => onSuccess(value.user, value.stateToken))
        .catch(async (response) => {
          if (response.status === 401) {
            setIsErrorChange(true);
          } else {
            addAlert({
              title: tErr("title"),
              message: tErr("server-error"),
              theme: "danger",
            });
          }
        });
    } else {
      setIsErrorChange(true);
    }
  };

  const onChangeHandler = (code: string) => {
    setPasscode(code);
    setIsErrorChange(false);
    sendConfirmCodeMutation.reset();
  };
  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        onSendConfirmCode();
      }}
    >
      <div className={formClasses}>
        <KeyField
          onChange={onChangeHandler}
          isError={isErrorChange}
          errorMessage={
            passcode.length !== 6
              ? `${t("error-contain")}`
              : `${t("error-incorrect")}`
          }
          disabled={sendConfirmCodeMutation.isPending || isLoading}
          autoFocus
        />
        <div className={styles["request-button-wrapper"]}>{children}</div>
        <Button
          view="action"
          className={styles["confirmation-form"]}
          loading={sendConfirmCodeMutation.isPending || isLoading}
          type="submit"
        >
          {t("confirm")}
        </Button>
      </div>
    </form>
  );
}

ConfirmationForm.defaultProps = {
  isLoading: false,
};
export default ConfirmationForm;
