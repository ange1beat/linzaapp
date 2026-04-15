import { IMember, isSupervisor } from "@/entities/members";
import { USER_ROLES } from "@/shared/config";

export function getRole(member: Pick<IMember, "roles">) {
  return isSupervisor(member) ? USER_ROLES.Supervisor : USER_ROLES.User;
}
