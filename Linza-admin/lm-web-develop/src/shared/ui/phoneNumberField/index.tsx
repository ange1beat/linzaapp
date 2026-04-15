import React from "react";

import { phoneNumberFormatter } from "@/shared/lib/phoneNumber";
import { Input } from "@/shared/ui";

interface IPhoneNumberField {
  isError: boolean;
  autoFocus?: boolean;
  errorMessage: string;
  placeholder: string;
  onChange: ({}: IFormatPhone) => void;
}
interface IFormatPhone {
  phone: string;
  isValid: boolean;
}
function PhoneNumberField({
  onChange,
  isError,
  errorMessage,
  placeholder,
  autoFocus,
}: IPhoneNumberField) {
  const [inputValue, setInputValue] = React.useState("");
  const onChangeHandler = (val: string) => {
    const formattedNumber = phoneNumberFormatter(val);
    onChange({
      ...formattedNumber,
      phone: formattedNumber.phone.replaceAll(" ", ""),
    });
    setInputValue(val);
  };

  return (
    <Input
      autoFocus={autoFocus}
      value={phoneNumberFormatter(inputValue).phone}
      placeholder={placeholder}
      onChange={onChangeHandler}
      isError={isError}
      errorMessage={errorMessage}
    />
  );
}

export default PhoneNumberField;
