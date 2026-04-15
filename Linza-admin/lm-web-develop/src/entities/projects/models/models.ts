import { z } from "zod";

export const project = z.object({
  id: z.string(),
  name: z.string(),
  createdBy: z.string(),
  createdAt: z.string().datetime(),
  avatarUrl: z.string().nullable(),
});

export const favoriteProject = z.object({
  id: z.string(),
  name: z.string().optional().nullable(),
  avatarUrl: z.string().optional().nullable(),
  isAvailable: z.boolean(),
});

export type IProject = z.infer<typeof project>;
export type IFavoriteProject = z.infer<typeof favoriteProject>;

export const projectNameSchema = z
  .string()
  .trim()
  .min(1, "project.min-length")
  .max(50, "project.max-length")
  .refine(
    (name) => /^[a-zA-Zа-яА-Я0-9_ -]*$/.test(name),
    "project.special-characters-only",
  );

export const projectsOfMemberSchema = z.object({
  userId: z.string(),
  projectIds: z.array(z.string()),
});
