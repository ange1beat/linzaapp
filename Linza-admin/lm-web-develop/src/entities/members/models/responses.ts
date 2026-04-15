import { z } from "zod";

import { USER_ROLES } from "@/shared/config";

/**
 * Member schema that accepts snake_case from linza-board backend
 * and transforms to camelCase for frontend usage.
 * Maps portal_roles to User/Supervisor role system.
 */
export const memberSchema = z
  .object({
    id: z.union([z.string(), z.number()]).transform(String),
    firstName: z.string().optional(),
    first_name: z.string().optional(),
    lastName: z.string().optional(),
    last_name: z.string().optional(),
    email: z.string().email(),
    phoneNumber: z.string().nullable().optional(),
    phone_number: z.string().nullable().optional(),
    telegramUsername: z.string().nullable().optional(),
    telegram_username: z.string().nullable().optional(),
    roles: z.array(z.string()).optional(),
    portal_roles: z.array(z.string()).optional(),
    avatarUrl: z.string().nullable().optional(),
    avatar_url: z.string().nullable().optional(),
    lastLoginDate: z.string().nullable().optional(),
    last_login_at: z.string().nullable().optional(),
    login: z.string().optional(),
    role: z.string().optional(),
    tenant_id: z.number().nullable().optional(),
    team_id: z.number().nullable().optional(),
    created_by: z.number().nullable().optional(),
  })
  .transform((data) => {
    // Map portal_roles to User/Supervisor system
    let roles: string[] = data.roles ?? [];
    if (!roles.length && data.portal_roles?.length) {
      const hasAdmin = data.portal_roles.includes("administrator");
      roles = hasAdmin
        ? [USER_ROLES.Supervisor]
        : [USER_ROLES.User];
    }
    if (!roles.length && data.role) {
      roles =
        data.role === "superadmin" || data.role === "admin"
          ? [USER_ROLES.Supervisor]
          : [USER_ROLES.User];
    }

    return {
      id: String(data.id),
      firstName: data.firstName || data.first_name || "",
      lastName: data.lastName || data.last_name || "",
      email: data.email,
      phoneNumber: data.phoneNumber ?? data.phone_number ?? null,
      telegramUsername:
        data.telegramUsername ?? data.telegram_username ?? null,
      roles,
      avatarUrl: data.avatarUrl ?? data.avatar_url ?? null,
      lastLoginDate: data.lastLoginDate ?? data.last_login_at ?? null,
    };
  });

export const membersSchema = z.object({
  users: z.array(memberSchema),
  total: z.number(),
});

export const membersInProjectSchema = z
  .object({
    // New backend returns array of member objects, not just userIds
    userIds: z.array(z.string()).optional(),
  })
  .passthrough()
  .transform((data) => {
    // If backend returns full member list, extract IDs
    if (data.userIds) return { userIds: data.userIds };
    // Fallback for new format (array of objects with user_id)
    return { userIds: [] };
  });
