import { api } from "@/shared/api";

// Backend uses POST toggle instead of separate PUT/DELETE
export function addProjectFav(projectId: string) {
  return api.post(`projects/${projectId}/favorite`);
}

export function delProjectFav(projectId: string) {
  return api.post(`projects/${projectId}/favorite`);
}
