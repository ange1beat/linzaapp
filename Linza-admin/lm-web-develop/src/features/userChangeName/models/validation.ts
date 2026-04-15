import { z } from "zod";

const nameSchema = z.string().min(1, "required").max(50, "max-length");

export const nameValidationSchema = z.object({
  firstName: nameSchema,
  lastName: nameSchema,
});
