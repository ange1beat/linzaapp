import React from "react";

import { Persona as GPersona } from "@gravity-ui/uikit";
import cn from "classnames";

import styles from "./Persona.module.scss";

interface IPersonaProps {
  className?: string;
  text: string;
  image?: string | null;
  size?: "n" | "s" | "xs" | "xxs";
  disabled?: boolean;
  onClick?: () => void;
  defaultImage?: string;
}

function Persona({
  className,
  size,
  onClick,
  text,
  image,
  disabled,
  defaultImage,
}: IPersonaProps) {
  const classes = cn(
    styles.persona,
    {
      [styles["persona--xxs"]]: size === "xxs",
      [styles["persona--xs"]]: size === "xs",
      [styles["persona--s"]]: size === "s",
      [styles["persona--n"]]: size === "n",
      [styles["persona--disabled"]]: disabled,
    },
    className,
  );

  return (
    <GPersona
      onClick={onClick}
      text={text}
      image={image || defaultImage}
      className={classes}
      hasBorder={false}
    />
  );
}

Persona.defaultProps = {
  size: "n" as "n" | "s",
};

export default Persona;
