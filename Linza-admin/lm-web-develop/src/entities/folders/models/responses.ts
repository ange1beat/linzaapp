import { z } from "zod";

export const folderSchema = z.object({
  id: z.string(),
  name: z.string(),
});

export const getFoldersResponseSchema = z.object({
  folders: z.array(folderSchema),
  total: z.number(),
});
