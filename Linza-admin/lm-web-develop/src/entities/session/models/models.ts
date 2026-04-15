import { z } from "zod";

export const userLogin = z.object({
  id: z.string(),
  email: z.string().email(),
  phoneNumber: z.string().nullable(),
});

export type IUserLogin = z.infer<typeof userLogin>;
