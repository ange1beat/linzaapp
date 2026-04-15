import React from "react";

import { Trans, useTranslation } from "react-i18next";

import { AuthResult } from "@/entities/auth";
import { ROUTES } from "@/shared/config";

import styles from "./RegistrationSuccessPage.module.scss";

function RegistrationSuccessPage() {
  const { t } = useTranslation("pages.registrationSuccessPage");
  return (
    <div className={styles["registration-success-page"]}>
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

export default RegistrationSuccessPage;
