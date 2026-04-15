import { IMember } from "@/entities/members";
import { USER_ROLES } from "@/shared/config";

export function isSupervisor(member: Pick<IMember, "roles">) {
  return member.roles.includes(USER_ROLES.Supervisor);
}
