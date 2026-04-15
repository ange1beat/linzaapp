import { z } from "zod";

export const addMemberRequestErrorsSchema = z.object({
  errors: z.object({
    email: z.array(z.string()),
  }),
});
