import { api } from "@/shared/api";

export function changeMemberRole({
  memberId,
  isSupervisor,
}: {
  memberId: string;
  isSupervisor: boolean;
}) {
  return api.patch(`users/${memberId}/roles`, {
    json: { isSupervisor },
  });
}
