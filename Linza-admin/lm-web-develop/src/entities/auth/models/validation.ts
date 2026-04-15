import { isValidNumber } from "libphonenumber-js";
import { z } from "zod";

import { KEY_FIELD_LENGTH } from "@/shared/ui";

export const passwordSchema = z
  .string()
  .trim()
  .min(1, "password.required")
  .min(8, "password.min-length")
  .max(50, "password.max-length")
  .refine((p) => /^(?=.*[A-Z]).+$/g.test(p), {
    message: "password.uppercase",
  })
  .refine((p) => /^(?=.*[a-z]).+$/g.test(p), {
    message: "password.lowercase",
  })
  .refine((v) => /^(?=.*[0-9]).+$/g.test(v), {
    message: "password.numbers",
  })
  .refine((v) => /^(?=.*[\W_]).+$/g.test(v), {
    message: "password.non-alphanumeric",
  });

export const passwordMatch: [
  (data: { password: string; confirmPassword: string }) => boolean,
  params?: { message: string; path: string[] },
] = [
  (data) => {
    return data.password === data.confirmPassword;
  },
  {
    message: "password.confirm-password-different",
    path: ["confirmPassword"],
  },
];

export const otpFormSchema = z.object({
  otp: z
    .string()
    .min(KEY_FIELD_LENGTH, "otp.length")
    .max(KEY_FIELD_LENGTH, "otp.length"),
});

export const emailSchema = z
  .string({ required_error: "email.required" })
  .trim()
  .min(1, "email.required")
  .email("email.invalid-email");

export const phoneSchema = z
  .string({ required_error: "phone.required" })
  .trim()
  .min(1, "phone.required")
  .refine(isValidNumber, "phone.invalid-phone");
