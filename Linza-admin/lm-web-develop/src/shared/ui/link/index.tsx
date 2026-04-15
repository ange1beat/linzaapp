import React from "react";

import classNames from "classnames";
import { Link as RLink } from "react-router-dom";

import styles from "./Link.module.scss";

interface ILink {
  className?: string;
  href: string;
  target?: "_self" | "_blank" | "_parent" | "_top";
  children: React.ReactNode;
  disabled?: boolean;
}

const defaultProps: Partial<ILink> = { target: "_self" };

function Link({ className, href, target, disabled, children }: ILink) {
  const onClickHandler = (e: React.MouseEvent<HTMLElement>) => {
    e.stopPropagation();
  };

  const classes = classNames(
    styles.link,
    { [styles.disabled]: disabled },
    className,
  );
  return (
    <RLink
      className={classes}
      to={href}
      target={target}
      onClick={onClickHandler}
    >
      {children}
    </RLink>
  );
}

Link.defaultProps = defaultProps;

export default Link;
