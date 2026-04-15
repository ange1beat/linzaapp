import { UserChangePassword } from "@/features/userChangePassword";

import styles from "./UserChangePasswordPage.module.scss";

function UserChangePasswordPage() {
  return (
    <div className={styles["user-change-password-page"]}>
      <UserChangePassword />
    </div>
  );
}

export default UserChangePasswordPage;
