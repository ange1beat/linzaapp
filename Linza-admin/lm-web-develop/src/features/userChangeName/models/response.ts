import { z } from "zod";

export const updateUserNameResponse = z.object({
  errors: z.object({
    firstName: z.array(z.string()).optional(),
    lastName: z.array(z.string()).optional(),
  }),
});
