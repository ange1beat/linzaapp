import { UserChangeTelegram } from "@/features/userChangeTelegram";

import styles from "./UserChangeTelegramPage.module.scss";

function UserChangeTelegramPage() {
  return (
    <div className={styles["user-change-telegram-page"]}>
      <UserChangeTelegram />
    </div>
  );
}

export default UserChangeTelegramPage;
