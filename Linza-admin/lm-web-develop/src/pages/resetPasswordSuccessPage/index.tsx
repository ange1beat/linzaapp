import React from "react";

import { Trans, useTranslation } from "react-i18next";

import { AuthResult } from "@/entities/auth";
import { ROUTES } from "@/shared/config";

import styles from "./ResetPasswordSuccessPage.module.scss";

function ResetPasswordSuccessPage() {
  const { t } = useTranslation("pages.resetPasswordSuccessPage");
  return (
    <div className={styles["reset-password-success-page"]}>
      <AuthResult
        title={t("title")}
        isSuccess
        header={<Trans i18nKey={"header"} t={t} />}
        linkText={t("link-text")}
        link={ROUTES.login}
        message={t("message")}
      />
    </div>
  );
}

export default ResetPasswordSuccessPage;
