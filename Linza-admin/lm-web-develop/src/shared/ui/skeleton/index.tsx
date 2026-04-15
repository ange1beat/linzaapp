import React from "react";

import { Skeleton as GSkeleton } from "@gravity-ui/uikit";
import cn from "classnames";

import styles from "./Skeleton.module.scss";

function Skeleton({
  className,
  isLoad,
  height,
  children,
}: {
  className?: string;
  isLoad: boolean;
  height: number;
  children?: React.ReactNode;
}) {
  const classes = cn(styles.skeleton, className);
  return isLoad ? (
    <GSkeleton className={classes} style={{ height }} />
  ) : (
    <>{children}</>
  );
}

export default Skeleton;
