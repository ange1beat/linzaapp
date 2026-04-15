import { z } from "zod";

export const verifyOTPResponse = z.object({
  recoveryToken: z.string(),
});

export const setPasswordErrors = z.object({
  errors: z.object({
    newPassword: z.array(z.string()),
  }),
});
