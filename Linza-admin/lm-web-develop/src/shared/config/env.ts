import { z } from "zod";

export default z
  .object({
    API_URL: z.string(),
    RE_REQUEST_SECONDS: z.number().default(60),
  })
  .parse({
    API_URL: import.meta.env.VITE_API_URL,
    RE_REQUEST_SECONDS: Number(import.meta.env.VITE_REQUEST_AGAIN_SECONDS),
  });
