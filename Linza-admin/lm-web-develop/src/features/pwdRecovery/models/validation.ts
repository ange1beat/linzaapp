import { z } from "zod";

import { passwordMatch, passwordSchema } from "@/entities/auth/models";
import { validatePhoneNumber } from "@/shared/lib/phoneNumber";

export const sendCodeForResetPasswordSchema = z.object({
  login: z
    .string()
    .trim()
    .min(1, "login.empty")
    .refine(
      (value) => /^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$/.test(value),
      "login.invalid",
    )
    .or(
      z
        .string()
        .trim()
        .min(1, "login.empty")
        .refine((value) => validatePhoneNumber(value), "login.invalid"),
    ),
});

export const passwordMatchSchema = z
  .object({
    password: passwordSchema,
    confirmPassword: z.string(),
  })
  .refine(...passwordMatch);
