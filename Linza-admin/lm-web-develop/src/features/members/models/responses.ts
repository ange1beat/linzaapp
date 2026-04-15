import { z } from "zod";

export const editMemberPasswordErrors = z.object({
  errors: z.object({
    newPassword: z.array(z.string()).optional(),
  }),
});
