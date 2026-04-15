import React from "react";

import { TextInput as GInput } from "@gravity-ui/uikit";
import cn from "classnames";

import styles from "./Input.module.scss";

interface IInput {
  className?: string;
  name?: string;
  value?: string;
  placeholder?: string;
  isError?: boolean;
  errorMessage?: string;
  disabled?: boolean;
  onChange: (v: string) => void;
  size?: "xl" | "l" | "m" | "s";
  ref?: React.Ref<HTMLInputElement>;
  rightContent?: React.ReactNode;
  autoFocus?: boolean;
  onKeyUp?: (e: React.KeyboardEvent<HTMLInputElement>) => void;
}

const ContainerRightContent = (props: React.PropsWithChildren) => (
  <div className={styles["input__right-content"]}>{props.children}</div>
);

function Input(
  { size = "xl", className, ...props }: IInput,
  ref: React.ForwardedRef<HTMLInputElement>,
) {
  const onChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    props.onChange(e.target.value);
  };
  const rightContentInput = () => {
    if (props.rightContent) {
      return (
        <ContainerRightContent>{props.rightContent}</ContainerRightContent>
      );
    }
  };
  const classes = cn(className, styles.input);
  return (
    <GInput
      {...props}
      className={classes}
      ref={ref}
      size={size}
      validationState={props.isError ? "invalid" : undefined}
      onChange={onChange}
      rightContent={rightContentInput()}
    />
  );
}

export default React.forwardRef(Input);
