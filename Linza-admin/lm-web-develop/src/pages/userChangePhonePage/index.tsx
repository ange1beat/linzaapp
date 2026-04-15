import { UserChangePhone } from "@/features/userChangePhone";

import styles from "./UserChangePhonePage.module.scss";

function UserChangePhonePage() {
  return (
    <div className={styles["user-change-phone-page"]}>
      <UserChangePhone />
    </div>
  );
}

export default UserChangePhonePage;
