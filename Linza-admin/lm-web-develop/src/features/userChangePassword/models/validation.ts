import { z } from "zod";

import { passwordMatch, passwordSchema } from "@/entities/auth/models";

export const updatePasswordSchema = z
  .object({
    currentPassword: z.string().min(1, { message: "password.required" }),
    password: passwordSchema,
    confirmPassword: z.string().min(1, { message: "password.required" }),
  })
  .refine(...passwordMatch);
