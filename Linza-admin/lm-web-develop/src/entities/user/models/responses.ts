import { z } from "zod";

const flexibleId = z.union([z.string(), z.number()]).transform(String);

export const userSchema = z.object({
  id: flexibleId,
  firstName: z.string(),
  lastName: z.string(),
  email: z.string().email(),
  phoneNumber: z.string().nullable(),
  telegramUsername: z.string().nullable(),
  avatarUrl: z.string().optional().nullable(),
  tenantId: flexibleId.optional().nullable(),
  teamId: flexibleId.optional().nullable(),
  portalRoles: z.array(z.string()).optional().default([]),
  activeRole: z.string().optional().nullable(),
  storageQuotaBytes: z.number().optional().default(0),
  storageUsedBytes: z.number().optional().default(0),
});
