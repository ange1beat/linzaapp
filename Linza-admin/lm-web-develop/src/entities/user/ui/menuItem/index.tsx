import React from "react";

import cn from "classnames";

import { defaultAva } from "@/entities/members";

import styles from "./UserMenuItem.module.scss";

function UserMenuItem({
  className,
  avatar,
  isSelected,
  onClick,
  onMouseDown,
  onTouchStart,
}: {
  className?: string;
  avatar?: string | null;
  isSelected: boolean;
  onClick: () => void;
  onMouseDown: (e: React.MouseEvent) => void;
  onTouchStart: (e: React.TouchEvent) => void;
}) {
  const classes = cn(className, styles["user-menu-item"], {
    [styles["user-menu-item--selected"]]: isSelected,
  });
  const userAvatar = avatar || defaultAva;
  return (
    <div
      className={classes}
      onClick={onClick}
      onMouseDown={onMouseDown}
      onTouchStart={onTouchStart}
    >
      <img
        className={styles["user-menu-item__img"]}
        src={userAvatar}
        alt="avatar"
      />
    </div>
  );
}

export default UserMenuItem;
