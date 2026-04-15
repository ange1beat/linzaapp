import { z } from "zod";

export const updateProjectNameResponse = z.object({
  errors: z.object({
    name: z.array(z.string()).optional(),
  }),
});
