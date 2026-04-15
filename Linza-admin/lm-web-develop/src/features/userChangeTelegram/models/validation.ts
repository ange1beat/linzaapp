import { z } from "zod";

export const telegramFormSchema = z.object({
  telegram: z
    .string()
    .trim()
    .startsWith("@", "telegram.start")
    .min(1, "telegram.min-length")
    .min(5, "telegram.min-length")
    .max(32, "telegram.max-length")
    .regex(/^@[a-zA-Z0-9_]+$/, "telegram.symbol"),
});
