import { z } from "zod";

export const createUserErrors = z.object({
  errors: z.object({
    firstName: z.array(z.string()).optional(),
    lastName: z.array(z.string()).optional(),
    password: z.array(z.string()).optional(),
  }),
});
