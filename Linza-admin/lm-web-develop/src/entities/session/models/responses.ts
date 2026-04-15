import { z } from "zod";

export const tokenResponse = z.object({
  accessToken: z.string(),
});
