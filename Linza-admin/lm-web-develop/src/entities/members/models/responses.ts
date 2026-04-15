import { z } from "zod";

import { USER_ROLES } from "@/shared/config";

export const memberSchema = z.object({
  id: z.string(),
  firstName: z.string(),
  lastName: z.string(),
  email: z.string().email(),
  phoneNumber: z.string().nullable().optional(),
  telegramUsername: z.string().nullable().optional(),
  roles: z.array(z.enum([USER_ROLES.User, USER_ROLES.Supervisor])),
  avatarUrl: z.string().nullable().optional(),
  lastLoginDate: z.string().nullable().optional(),
});

export const membersSchema = z.object({
  users: z.array(memberSchema),
  total: z.number(),
});

export const membersInProjectSchema = z.object({
  userIds: z.array(z.string()),
});
