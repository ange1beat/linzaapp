import { api } from "@/shared/api";

export async function deleteProject(projectId: string) {
  return api.delete(`projects/${projectId}`).json();
}
