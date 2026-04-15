import {
  formatIncompletePhoneNumber,
  isValidPhoneNumber,
  parseIncompletePhoneNumber,
} from "libphonenumber-js";

export function validatePhoneNumber(val: string) {
  const incompleteNumber = parseIncompletePhoneNumber(val);

  return isValidPhoneNumber(incompleteNumber);
}

function formatPhoneNumber(val: string) {
  return formatIncompletePhoneNumber(parseIncompletePhoneNumber(val));
}

export function phoneNumberFormatter(tel: string) {
  const reg = /[^+\d]/g;
  const phoneNumber = tel.replace(reg, "");

  if (phoneNumber) {
    if (phoneNumber[0] === "+") {
      return {
        phone: formatPhoneNumber(phoneNumber),
        isValid: validatePhoneNumber(phoneNumber),
      };
    } else if (phoneNumber[0] === "8") {
      return {
        phone: formatPhoneNumber(phoneNumber.replace(phoneNumber[0], "+7")),
        isValid: validatePhoneNumber(phoneNumber.replace(phoneNumber[0], "+7")),
      };
    } else {
      return {
        phone: formatPhoneNumber(`+${phoneNumber}`),
        isValid: validatePhoneNumber(`+${phoneNumber}`),
      };
    }
  } else {
    return {
      phone: "",
      isValid: false,
    };
  }
}
