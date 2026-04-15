import { UserChangeNameFeature } from "@/features/userChangeName";

import styles from "./UserChangeNamePage.module.scss";

function UserChangeNamePage() {
  return (
    <div className={styles["user-change-name-page"]}>
      <UserChangeNameFeature />
    </div>
  );
}

export default UserChangeNamePage;
