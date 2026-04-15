import { z } from "zod";

import { loginTypeSchema } from "@/entities/auth";
import { emailSchema, phoneSchema } from "@/entities/auth/models";

export const loginValidationSchema = z
  .string({ required_error: "login.empty" })
  .refine((data) => !!data, "login.empty")
  .refine((data) => {
    const isValidEmail = emailSchema.safeParse(data);
    const isValidPhone = phoneSchema.safeParse(data);
    return isValidEmail.success || isValidPhone.success;
  }, "login.invalid");

export const loginSchema = z.object({
  login: loginValidationSchema,
  password: z
    .string({ required_error: "password.empty" })
    .trim()
    .min(1, "password.empty"),
  loginType: loginTypeSchema,
});
