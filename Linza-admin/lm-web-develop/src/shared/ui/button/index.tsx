import React from "react";

import { Button as GButton } from "@gravity-ui/uikit";
import cn from "classnames";

import styles from "./Button.module.scss";

interface IButton {
  className?: string;
  view: "action" | "normal" | "outlined";
  href?: string;
  width?: "auto" | "max";
  loading?: boolean;
  disabled?: boolean;
  onClick?: () => void;
  size?: "xs" | "s" | "m" | "l" | "xl";
  type?: "button" | "submit";
  iconLeft?: React.ReactNode;
  iconRight?: React.ReactNode;
  tabIndex?: number;
}

const defaultProps: Partial<IButton> = {
  loading: false,
  disabled: false,
  size: "xl",
  type: "button",
};

function Button({
  iconLeft,
  iconRight,
  ...props
}: React.PropsWithChildren<IButton>) {
  const styleBtn = cn(
    {
      [styles["btn--primary"]]: props.view === "action",
      [styles["btn--loaded"]]: props.loading,
      [styles["btn__with-icon"]]: iconLeft || iconRight,
    },
    props.className,
  );
  return (
    <GButton {...props} className={styleBtn}>
      {iconLeft || iconRight ? (
        <div className={styles["btn__wrapper"]}>
          {iconLeft}
          {props.children}
          {iconRight}
        </div>
      ) : (
        <>{props.children}</>
      )}
    </GButton>
  );
}

Button.defaultProps = defaultProps;

export default Button;
