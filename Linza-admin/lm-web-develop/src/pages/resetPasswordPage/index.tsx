import React from "react";

import ResetPasswordWidget from "../../widgets/resetPassword";

import styles from "./ResetPasswordPage.module.scss";

function ResetPasswordPage() {
  return (
    <div className={styles["reset-password-page"]}>
      <ResetPasswordWidget />
    </div>
  );
}

export default ResetPasswordPage;
