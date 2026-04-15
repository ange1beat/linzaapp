import { z } from "zod";

export const storageQuotaSchema = z.object({
  id: z.number(),
  scope_type: z.string(),
  scope_id: z.number(),
  quota_bytes: z.number(),
  used_bytes: z.number(),
});

export type IStorageQuota = z.infer<typeof storageQuotaSchema>;

export const storageUsageSchema = z.object({
  user: storageQuotaSchema.nullable().optional(),
  team: storageQuotaSchema.nullable().optional(),
  tenant: storageQuotaSchema.nullable().optional(),
});

export type IStorageUsage = z.infer<typeof storageUsageSchema>;
