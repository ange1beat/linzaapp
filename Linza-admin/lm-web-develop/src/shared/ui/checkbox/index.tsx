import React from "react";

import { Checkbox as GCheckbox } from "@gravity-ui/uikit";
import cn from "classnames";

import styles from "./Checkbox.module.scss";

interface IProps {
  size: "m" | "l";
  checked: boolean;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  className?: string;
  disabled?: boolean;
}

function Checkbox(props: IProps) {
  const checkboxClasses = cn(
    styles.checkbox,
    {
      [styles["checkbox--checked"]]: props.checked,
      [styles["checkbox--disabled"]]: props.disabled,
    },
    props.className,
  );
  return <GCheckbox {...props} className={checkboxClasses} />;
}

export default Checkbox;
