import { z } from "zod";

export const sourceStatusErrorsSchema = z.object({
  errors: z.object({
    isActive: z.array(z.string()),
  }),
});
