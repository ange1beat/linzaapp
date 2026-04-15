import { z } from "zod";

export const tenantNameSchema = z.object({
  id: z.string(),
  name: z.string(),
});
