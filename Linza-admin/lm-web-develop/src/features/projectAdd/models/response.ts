import { z } from "zod";

export const newProjectErrors = z.object({
  errors: z.object({
    membersId: z.array(z.string()),
  }),
});
