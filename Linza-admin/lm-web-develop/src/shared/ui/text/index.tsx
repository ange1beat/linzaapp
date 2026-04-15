import React from "react";

import { Text as GText, TEXT_VARIANTS } from "@gravity-ui/uikit";
import classNames from "classnames";

import styles from "./Text.module.scss";

type CustomVariant = "modal-name" | "modal-email" | "filter";

interface IText {
  className?: string;
  children: React.ReactNode;
  variant: (typeof TEXT_VARIANTS)[number] | CustomVariant;
  ellipsis?: boolean;
}

function Text({ variant, className, children, ...props }: IText) {
  const cn = classNames(
    {
      [styles["body-1"]]: variant === "body-1",
      [styles["body-2"]]: variant === "body-2",
      [styles["body-3"]]: variant === "body-3",
      [styles["body-short"]]: variant === "body-short",
      [styles["caption-1"]]: variant === "caption-1",
      [styles["caption-2"]]: variant === "caption-2",
      [styles["header-1"]]: variant === "header-1",
      [styles["header-2"]]: variant === "header-2",
      [styles["subheader-1"]]: variant === "subheader-1",
      [styles["subheader-2"]]: variant === "subheader-2",
      [styles["subheader-3"]]: variant === "subheader-3",
      [styles["display-1"]]: variant === "display-1",
      [styles["display-2"]]: variant === "display-2",
      [styles["display-3"]]: variant === "display-3",
      [styles["display-4"]]: variant === "display-4",
      [styles["code-1"]]: variant === "code-1",
      [styles["code-2"]]: variant === "code-2",
      [styles["code-3"]]: variant === "code-3",
      [styles["code-inline-1"]]: variant === "code-inline-1",
      [styles["code-inline-2"]]: variant === "code-inline-2",
      [styles["code-inline-3"]]: variant === "code-inline-3",
      [styles["modal-name"]]: variant === "modal-name",
      [styles["modal-email"]]: variant === "modal-email",
      [styles.filter]: variant === "filter",
    },
    className,
  );
  return (
    <GText {...props} className={cn}>
      {children}
    </GText>
  );
}

export default Text;
