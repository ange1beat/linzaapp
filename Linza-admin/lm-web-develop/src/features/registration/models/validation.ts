import { z } from "zod";

import { passwordSchema } from "@/entities/auth/models";

export const createAccountSchema = z
  .object({
    firstName: z.string().trim().min(1, "required").max(50, "max-length"),
    lastName: z.string().trim().min(1, "required").max(50, "max-length"),
    password: passwordSchema,
    passwordConfirmation: z.string().trim().min(1, "required"),
  })
  .refine((field) => field.password === field.passwordConfirmation, {
    message: "password-confirm",
    path: ["passwordConfirmation"],
  });
