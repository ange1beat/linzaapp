import { z } from "zod";

export const newMemberSchema = z.object({
  email: z.string().min(1, "email.required").email("email.invalid-email"),
});
