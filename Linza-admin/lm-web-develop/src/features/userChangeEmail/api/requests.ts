import { api } from "@/shared/api";

export function updateUserEmail({
  email,
  otpValue,
}: {
  email: string;
  otpValue: string;
}) {
  return api.put("users/me/email", {
    json: {
      email: email.toLowerCase(),
      verificationCode: otpValue,
    },
  });
}

export function getChangeEmailOTP(data: { email: string; language: string }) {
  return api.post("users/me/email/change-request", {
    json: data,
  });
}
