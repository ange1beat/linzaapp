import React from "react";

import defaultProjectAvatar from "../../media/defaultProjectAvatar.svg";

import styles from "./MenuProjectItem.module.scss";

interface IMenuProjectItem {
  avatarUrl?: string | null;
}
function MenuProjectItem({ avatarUrl }: IMenuProjectItem) {
  return (
    <div className={styles["menu-item"]}>
      <img
        className={styles["menu-item__img"]}
        src={avatarUrl ?? defaultProjectAvatar}
        alt="project avatar"
      />
    </div>
  );
}

export default MenuProjectItem;
