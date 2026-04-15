import React, { useEffect, useRef } from "react";

import cn from "classnames";

import styles from "./KeyField.module.scss";

interface IKeyField {
  className?: string;
  isError?: boolean;
  errorMessage?: string;
  disabled?: boolean;
  onChange: (v: string) => void;
  autoFocus?: boolean;
}

export const KEY_FIELD_LENGTH = 6;
const inputProps: {
  type: "tel";
  inputMode: "numeric";
  pattern: string;
  min?: string;
  max?: string;
} = {
  type: "tel",
  inputMode: "numeric",
  pattern: "[0-9]{1}",
  min: "0",
  max: "9",
};

function KeyField({
  disabled,
  isError,
  errorMessage,
  className,
  onChange,
  autoFocus,
}: IKeyField) {
  const inputsRef = useRef<Array<HTMLInputElement>>([]);

  useEffect(() => {
    if (autoFocus) {
      inputsRef.current[0].focus();
    }
  }, []);

  const sendResult = () => {
    const res = inputsRef.current.map((input) => input.value).join("");
    onChange(res);
  };

  const handleOnChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const {
      target: { value, nextElementSibling },
    } = e;
    if (value.length > 1) {
      e.target.value = value.charAt(0);
      if (nextElementSibling !== null) {
        (nextElementSibling as HTMLInputElement).focus();
      }
    } else {
      if (value.match(inputProps.pattern)) {
        if (nextElementSibling !== null) {
          (nextElementSibling as HTMLInputElement).focus();
        }
      } else {
        e.target.value = "";
      }
    }
    sendResult();
  };

  const handleOnKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    const { key } = e;
    const target = e.target as HTMLInputElement;
    if (key === "Backspace") {
      if (target.value === "") {
        if (target.previousElementSibling !== null) {
          const t = target.previousElementSibling as HTMLInputElement;
          t.value = "";
          t.focus();
          e.preventDefault();
        }
      } else {
        target.value = "";
      }
      sendResult();
    }
  };

  const handleOnFocus = (e: React.FocusEvent<HTMLInputElement>) => {
    e.target.select();
  };

  const handleOnPaste = (e: React.ClipboardEvent<HTMLInputElement>) => {
    const pastedValue = e.clipboardData.getData("Text");

    let currentInput = 0;

    for (let i = 0; i < pastedValue.length; i++) {
      const pastedCharacter = pastedValue.charAt(i);
      if (pastedCharacter.match(inputProps.pattern)) {
        inputsRef.current[currentInput].value = pastedCharacter;
        if (inputsRef.current[currentInput].nextElementSibling !== null) {
          (
            inputsRef.current[currentInput]
              .nextElementSibling as HTMLInputElement
          ).focus();
          currentInput++;
        }
      }
    }
    sendResult();

    e.preventDefault();
  };

  const inputs = [];
  for (let i = 0; i < KEY_FIELD_LENGTH; i++) {
    inputs.push(
      <input
        key={i}
        onChange={handleOnChange}
        onKeyDown={handleOnKeyDown}
        onFocus={handleOnFocus}
        onPaste={handleOnPaste}
        {...inputProps}
        type="tel"
        ref={(el: HTMLInputElement) => {
          inputsRef.current[i] = el;
        }}
        maxLength={1}
        className={styles["key-field-container__input"]}
        autoComplete={i === 0 ? "one-time-code" : "off"}
        disabled={disabled}
        aria-label={`Character ${i + 1}.`}
      />,
    );
  }

  const classes = cn(styles["key-field-container"], className, {
    [styles["key-field-container--error"]]: isError,
  });
  return (
    <div className={classes}>
      <div className={styles["key-field-container__inputs"]}>{inputs}</div>
      {isError && (
        <span className={styles["key-field-container__error-message"]}>
          {errorMessage}
        </span>
      )}
    </div>
  );
}

export default KeyField;
