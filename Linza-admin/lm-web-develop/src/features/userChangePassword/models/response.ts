import { z } from "zod";

export const updateUserPasswordsErrors = z.object({
  errors: z.object({
    currentPassword: z.array(z.string()).optional(),
    newPassword: z.array(z.string()).optional(),
  }),
});
