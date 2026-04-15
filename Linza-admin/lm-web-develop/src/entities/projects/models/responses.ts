import { z } from "zod";

import { favoriteProject, project } from "./models";

export const projectsResponse = z.object({
  projects: z.array(project),
  total: z.number(),
});

export const favoriteProjectsResponse = z.object({
  favorites: z.array(favoriteProject),
});
