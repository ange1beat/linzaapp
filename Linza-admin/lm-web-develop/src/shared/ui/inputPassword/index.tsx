import React, { ForwardedRef, forwardRef } from "react";

import { Eye, EyeSlash } from "@gravity-ui/icons";
import { TextInput as GInputPass } from "@gravity-ui/uikit";
import cn from "classnames";

import styles from "./InputPassword.module.scss";

interface IInputPassword {
  className?: string;
  disabled?: boolean;
  errorMessage?: string;
  isError?: boolean;
  name?: string;
  onChange: (val: string) => void;
  placeholder?: string;
  ref: React.Ref<HTMLInputElement>;
  size?: "xl" | "l" | "m" | "s";
  value: string;
  autoFocus?: boolean;
}

function InputPassword(
  { size = "xl", className, ...props }: IInputPassword,
  ref: ForwardedRef<HTMLInputElement>,
) {
  const [hiddenValue, setHiddenValue] = React.useState(true);
  const changeValueVisionHandler = () => {
    setHiddenValue(!hiddenValue);
  };

  const onChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    props.onChange(e.target.value);
  };

  const classes = cn(className, styles["input-password"]);
  return (
    <GInputPass
      {...props}
      validationState={props.isError ? "invalid" : undefined}
      className={classes}
      type={hiddenValue ? "password" : "string"}
      onChange={onChange}
      size={size}
      ref={ref}
      rightContent={
        hiddenValue ? (
          <Eye
            className={styles["input-password__toggle-eye-icon"]}
            onClick={changeValueVisionHandler}
          />
        ) : (
          <EyeSlash
            className={styles["input-password__toggle-eye-icon"]}
            onClick={changeValueVisionHandler}
          />
        )
      }
    />
  );
}

export default forwardRef(InputPassword);
