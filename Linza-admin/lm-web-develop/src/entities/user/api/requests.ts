import { api } from "@/shared/api";

import { userSchema } from "../models/responses";

export function getUser() {
  return api.get("users/me").json().then(userSchema.parse);
}
