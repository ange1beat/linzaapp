import { z } from "zod";

export const loginTypeSchema = z.enum(["email", "phone"]);
export type LoginType = z.infer<typeof loginTypeSchema>;
export {
  emailSchema,
  phoneSchema,
  passwordSchema,
  passwordMatch,
} from "./validation";
