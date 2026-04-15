import { useMutation } from "@tanstack/react-query";

import { api } from "@/shared/api";

export async function updateUserPhone({
  phone,
  otpValue,
}: {
  phone: string;
  otpValue: string;
}) {
  return api.put("users/me/phone", {
    json: {
      phoneNumber: phone,
      verificationCode: otpValue,
    },
  });
}

export function getChangePhoneOTP(data: {
  phoneNumber: string;
  language: string;
}) {
  return api.post("users/me/phone/change-request", {
    json: data,
  });
}
