import { z } from "zod";

export const memberPasswordSchema = z
  .string({ required_error: "required" })
  .min(8, "min-length")
  .max(32, "max-length")
  .refine((value) => /[A-Z]/.test(value), {
    message: "contain-uppercase",
  })
  .refine((value) => /[a-z]/.test(value), {
    message: "contain-lowercase",
  })
  .refine((value) => /[!@#$%^&*(),.?":{}|<>]/.test(value), {
    message: "contain-special",
  });

export const validationMemberPassword = z
  .object({
    newPassword: memberPasswordSchema,
    confirmPassword: memberPasswordSchema,
  })
  .refine((data) => data.confirmPassword === data.newPassword, {
    message: "confirm-password-different",
    path: ["confirmPassword"],
  });
