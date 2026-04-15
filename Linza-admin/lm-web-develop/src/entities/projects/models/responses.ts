import { z } from "zod";

import { favoriteProject, project } from "./models";

export const projectSchema = project;

export const projectsResponse = z.object({
  projects: z.array(project),
  total: z.number(),
});

/**
 * Favorites response: backend returns array of projects directly,
 * not wrapped in { favorites: [...] }.
 */
export const favoriteProjectsResponse = z
  .union([
    // New format: array of projects
    z.array(favoriteProject),
    // Old format: { favorites: [...] }
    z.object({ favorites: z.array(favoriteProject) }),
  ])
  .transform((data) => {
    if (Array.isArray(data)) {
      return { favorites: data };
    }
    return data;
  });
