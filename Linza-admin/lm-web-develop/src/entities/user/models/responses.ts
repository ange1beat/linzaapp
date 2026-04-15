import { z } from "zod";

const flexibleId = z.union([z.string(), z.number()]).transform(String);

/**
 * User schema that accepts snake_case from linza-board backend
 * and transforms to camelCase for frontend usage.
 */
export const userSchema = z
  .object({
    id: flexibleId,
    // Accept both camelCase and snake_case
    firstName: z.string().optional(),
    first_name: z.string().optional(),
    lastName: z.string().optional(),
    last_name: z.string().optional(),
    email: z.string().email(),
    phoneNumber: z.string().nullable().optional(),
    phone_number: z.string().nullable().optional(),
    telegramUsername: z.string().nullable().optional(),
    telegram_username: z.string().nullable().optional(),
    avatarUrl: z.string().nullable().optional(),
    avatar_url: z.string().nullable().optional(),
    tenantId: flexibleId.optional().nullable(),
    tenant_id: z.union([z.string(), z.number()]).optional().nullable(),
    teamId: flexibleId.optional().nullable(),
    team_id: z.union([z.string(), z.number()]).optional().nullable(),
    portalRoles: z.array(z.string()).optional(),
    portal_roles: z.array(z.string()).optional(),
    activeRole: z.string().nullable().optional(),
    active_role: z.string().nullable().optional(),
    storageQuotaBytes: z.number().optional(),
    storage_quota_bytes: z.number().optional(),
    storageUsedBytes: z.number().optional(),
    storage_used_bytes: z.number().optional(),
    // Extra fields from backend
    login: z.string().optional(),
    role: z.string().optional(),
  })
  .transform((data) => ({
    id: String(data.id),
    firstName: data.firstName || data.first_name || "",
    lastName: data.lastName || data.last_name || "",
    email: data.email,
    phoneNumber: data.phoneNumber ?? data.phone_number ?? null,
    telegramUsername:
      data.telegramUsername ?? data.telegram_username ?? null,
    avatarUrl: data.avatarUrl ?? data.avatar_url ?? null,
    tenantId: data.tenantId ?? (data.tenant_id ? String(data.tenant_id) : null),
    teamId: data.teamId ?? (data.team_id ? String(data.team_id) : null),
    portalRoles: data.portalRoles ?? data.portal_roles ?? [],
    activeRole: data.activeRole ?? data.active_role ?? null,
    storageQuotaBytes: data.storageQuotaBytes ?? data.storage_quota_bytes ?? 0,
    storageUsedBytes: data.storageUsedBytes ?? data.storage_used_bytes ?? 0,
    login: data.login,
    role: data.role,
  }));

export type IUser = z.output<typeof userSchema>;
