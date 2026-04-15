import React from "react";

import classNames from "classnames";

import MenuWidget from "../../widgets/menuWidget";

import styles from "./MenuLayout.module.scss";

function MenuLayout({
  children,
  className,
}: {
  className?: string;
  children: React.ReactNode;
}) {
  const classes = classNames(styles["menu-layout"], className);
  return (
    <div className={classes}>
      <MenuWidget className={styles["menu-layout__menu"]} />
      <div className={styles["menu-layout__content"]}>{children}</div>
    </div>
  );
}

export default MenuLayout;
