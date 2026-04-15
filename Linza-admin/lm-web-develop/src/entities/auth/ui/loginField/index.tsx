import React from "react";

import { formatIncompletePhoneNumber, isValidNumber } from "libphonenumber-js";

import Input from "@/shared/ui/input";

import { emailSchema, LoginType } from "../../models";

function LoginField({
  isError,
  errorMessage,
  disabled,
  onChange,
  className,
  placeholder,
}: {
  placeholder?: string;
  isError?: boolean;
  errorMessage?: string;
  disabled?: boolean;
  className?: string;
  onChange: (v: string, type?: LoginType) => void;
}) {
  const rawValue = (value: string) => value.replaceAll(" ", "");
  const [inputValue, setInputValue] = React.useState("");
  const inputValueFormatted = isValidNumber(rawValue(inputValue))
    ? formatIncompletePhoneNumber(inputValue)
    : rawValue(inputValue);
  const handleInputChange = (val: string) => {
    let inputType: "email" | "phone" | undefined;

    if (emailSchema.safeParse(rawValue(val)).success) {
      inputType = "email";
      setInputValue(rawValue(val));
    } else if (isValidNumber(rawValue(val))) {
      setInputValue(rawValue(val));
      inputType = "phone";
    } else {
      inputType = undefined;
      setInputValue(rawValue(val));
    }
    onChange(rawValue(val), inputType);
  };

  return (
    <Input
      name="login"
      value={inputValueFormatted}
      onChange={handleInputChange}
      disabled={disabled}
      isError={isError}
      placeholder={placeholder}
      errorMessage={errorMessage}
      className={className}
      autoFocus
    />
  );
}

export default LoginField;
