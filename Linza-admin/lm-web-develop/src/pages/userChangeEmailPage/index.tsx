import { UserChangeEmail } from "@/features/userChangeEmail";

import styles from "./UserChangeEmailPage.module.scss";

function UserChangeEmailPage() {
  return (
    <div className={styles["user-change-email-page"]}>
      <UserChangeEmail />
    </div>
  );
}

export default UserChangeEmailPage;
