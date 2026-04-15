import { z } from "zod";

import { userLogin } from "@/entities/session";

export const loginResponse = z.object({
  user: userLogin,
  stateToken: z.string(),
});

export const verificationOtpResponse = z.object({
  stateToken: z.string(),
});

export const sendOtpCodeResponse = z.object({
  user: userLogin,
  stateToken: z.string(),
});
