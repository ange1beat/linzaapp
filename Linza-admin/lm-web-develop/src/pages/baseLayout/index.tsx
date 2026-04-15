import React from "react";

import classNames from "classnames";

import styles from "./BaseLayout.module.scss";

function BaseLayout({
  children,
  className,
}: {
  className?: string;
  children: React.ReactNode;
}) {
  const classes = classNames(styles["base-layout"], className);
  return <div className={classes}>{children}</div>;
}

export default BaseLayout;
