import { z } from "zod";

const flexibleId = z.union([z.string(), z.number()]).transform(String);

/**
 * Project schema — accepts snake_case from linza-board backend.
 */
export const project = z
  .object({
    id: flexibleId,
    name: z.string(),
    createdBy: z.string().optional(),
    created_by: z.union([z.string(), z.number()]).optional().nullable(),
    createdAt: z.string().optional(),
    created_at: z.string().optional().nullable(),
    avatarUrl: z.string().nullable().optional(),
    avatar_url: z.string().nullable().optional(),
    tenant_id: z.number().optional(),
    is_favorite: z.boolean().optional(),
  })
  .transform((data) => ({
    id: String(data.id),
    name: data.name,
    createdBy: data.createdBy || (data.created_by ? String(data.created_by) : ""),
    createdAt: data.createdAt || data.created_at || "",
    avatarUrl: data.avatarUrl ?? data.avatar_url ?? null,
    isFavorite: data.is_favorite ?? false,
  }));

export const favoriteProject = z
  .object({
    id: flexibleId,
    name: z.string().optional().nullable(),
    avatarUrl: z.string().optional().nullable(),
    avatar_url: z.string().optional().nullable(),
    isAvailable: z.boolean().optional(),
    is_favorite: z.boolean().optional(),
  })
  .transform((data) => ({
    id: String(data.id),
    name: data.name ?? null,
    avatarUrl: data.avatarUrl ?? data.avatar_url ?? null,
    isAvailable: data.isAvailable ?? data.is_favorite ?? true,
  }));

export type IProject = z.output<typeof project>;
export type IFavoriteProject = z.output<typeof favoriteProject>;

export const projectNameSchema = z
  .string()
  .trim()
  .min(1, "project.min-length")
  .max(50, "project.max-length")
  .refine(
    (name) => /^[a-zA-Zа-яА-Я0-9_ -]*$/.test(name),
    "project.special-characters-only",
  );

export const projectsOfMemberSchema = z
  .object({
    userId: z.string().optional(),
    user_id: z.union([z.string(), z.number()]).optional(),
    projectIds: z.array(z.string()).optional(),
    project_ids: z.array(z.number()).optional(),
  })
  .transform((data) => ({
    userId: data.userId || (data.user_id ? String(data.user_id) : ""),
    projectIds: data.projectIds || (data.project_ids?.map(String) ?? []),
  }));
