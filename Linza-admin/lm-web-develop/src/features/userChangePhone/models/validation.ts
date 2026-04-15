import { z } from "zod";

export const phoneFormSchema = z
  .object({
    phone: z.string().min(1, "phone.required"),
    isValid: z.boolean(),
  })
  .refine((data) => data.isValid, {
    message: "phone.invalid-phone",
    path: ["phone"],
  });
