import { z } from "zod";

export const telegramError = z.object({
  errors: z.object({
    username: z.array(z.string()).nullable(),
  }),
});
