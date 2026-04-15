import { api } from "@/shared/api";

import { tenantNameSchema } from "../models/responses";

export function getTenantName() {
  return api.get("tenants/my").json().then(tenantNameSchema.parse);
}
