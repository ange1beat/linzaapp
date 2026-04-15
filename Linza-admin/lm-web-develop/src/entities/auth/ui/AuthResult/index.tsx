import React from "react";

import cn from "classnames";

import { Button, Link, Text, WindowFrame } from "@/shared/ui";

import styles from "./AuthResult.module.scss";

interface IProps {
  header: React.ReactNode;
  title: string;
  message: string;
  link: string;
  linkText: string;
  isSuccess: boolean;
}

function AuthResult({
  header,
  title,
  message,
  link,
  linkText,
  isSuccess,
}: IProps) {
  const classes = cn(styles["auth-result-window__status"], {
    [styles["status-success"]]: isSuccess,
    [styles["status-unsuccess"]]: !isSuccess,
  });
  return (
    <WindowFrame title={header}>
      <div className={styles["auth-result-window"]}>
        <div className={styles["auth-result-window__text-block"]}>
          <Text variant="subheader-3" className={classes}>
            {title}
          </Text>
          <Text
            variant="body-2"
            className={styles["auth-result-window__message"]}
          >
            {message}
          </Text>
        </div>
        <Button view="action" width="max">
          <Link href={link} className={styles["auth-result-window__link"]}>
            {linkText}
          </Link>
        </Button>
      </div>
    </WindowFrame>
  );
}

export default AuthResult;
