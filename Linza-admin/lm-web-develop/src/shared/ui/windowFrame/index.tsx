import React from "react";

import cn from "classnames";

import Text from "../text";

import styles from "./windowFrame.module.scss";

interface IWindowFrame {
  className?: string;
  children: React.ReactNode;
  title: React.ReactNode;
}

function WindowFrame({ className, title, children }: IWindowFrame) {
  const classes = cn(styles.window, className);
  return (
    <div className={classes}>
      <Text className={styles["window__title"]} variant="header-1">
        {title}
      </Text>
      <div className={styles["window__form"]}> {children}</div>
    </div>
  );
}

export default WindowFrame;
