import { useEffect, useState, KeyboardEvent } from "react";

import { Check, Xmark } from "@gravity-ui/icons";

import { Button, Input } from "@/shared/ui";

import styles from "./InputConfirm.module.scss";

function InputConfirm(props: {
  className?: string;
  name?: string;
  value: string;
  placeholder?: string;
  isError?: boolean;
  errorMessage?: string;
  disabled?: boolean;
  onChange?: (v: string) => void;
  onApply: (v: string) => void;
  autoFocus?: boolean;
  loading?: boolean;
}) {
  const [value, setValue] = useState(props.value);

  useEffect(() => {
    setValue(props.value);
  }, [props.value]);

  useEffect(() => {
    props.onChange?.(value);
  }, [value]);

  const onApply = () => {
    props.onApply(value);
  };

  const onCancel = () => {
    setValue(props.value);
  };

  const onKeyUpHandler = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      props.onApply(value);
    } else if (e.key === "Escape") {
      setValue(props.value);
    }
  };

  let rightContentInput = null;
  if (value !== props.value) {
    rightContentInput = (
      <div className={styles["input-confirm__buttons"]}>
        <Button
          view="normal"
          size="l"
          iconRight={<Xmark />}
          onClick={onCancel}
          loading={props.loading}
        />
        <Button
          view="action"
          size="l"
          iconRight={<Check />}
          onClick={onApply}
          loading={props.loading}
        />
      </div>
    );
  }
  return (
    <Input
      {...props}
      disabled={props.disabled || props.loading}
      size="xl"
      value={value}
      rightContent={rightContentInput}
      onChange={setValue}
      onKeyUp={onKeyUpHandler}
    />
  );
}

export default InputConfirm;
