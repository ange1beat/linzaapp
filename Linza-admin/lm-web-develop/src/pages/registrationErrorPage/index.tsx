import React from "react";

import { Trans, useTranslation } from "react-i18next";

import { AuthResult } from "@/entities/auth";
import { ROUTES } from "@/shared/config";

import styles from "./RegistrationErrorPage.module.scss";

function RegistrationErrorPage() {
  const { t } = useTranslation("pages.registrationErrorPage");
  return (
    <div className={styles["registration-error-page"]}>
      <AuthResult
        title={t("title")}
        isSuccess={false}
        header={<Trans i18nKey={"header"} t={t} />}
        linkText={t("link-text")}
        link={ROUTES.login}
        message={t("message")}
      />
    </div>
  );
}

export default RegistrationErrorPage;
