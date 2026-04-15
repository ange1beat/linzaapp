import { z } from "zod";

import { getFoldersResponseSchema } from "@/entities/folders/models/responses";
import { api } from "@/shared/api";

export function getFolders(data: {
  projectId: string;
  name?: string;
  pageSize: number;
  pageNumber: number;
}): Promise<z.infer<typeof getFoldersResponseSchema>> {
  const searchParams = new URLSearchParams();
  data.name && searchParams.set("name", data.name);
  searchParams.set("pageSize", data.pageSize.toString());
  searchParams.set("pageNumber", data.pageNumber.toString());
  return api.get(`projects/${data.projectId}/folders`, { searchParams }).json();
}

export function deleteFolder(data: { projectId: string; folderId: string }) {
  const { projectId, folderId } = data;
  return api.delete(`projects/${projectId}/folders/${folderId}`);
}
