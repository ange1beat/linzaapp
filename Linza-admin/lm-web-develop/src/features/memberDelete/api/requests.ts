import { api } from "@/shared/api";

export function deleteMember({ id }: { id: string }) {
  return api.delete(`users/${id}`).json();
}
