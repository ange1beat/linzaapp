import { api } from "@/shared/api";

export function addProjectFav(projectId: string) {
  return api.put(`projects/favorites/${projectId}`);
}

export function delProjectFav(projectId: string) {
  return api.delete(`projects/favorites/${projectId}`);
}
