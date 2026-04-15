import { api } from "@/shared/api";

interface SwitchRoleResponse {
  access_token: string;
  token_type: string;
}

export const switchPortalRole = async (
  activeRole: string,
): Promise<SwitchRoleResponse> => {
  return api
    .post("auth/switch-role", { json: { active_role: activeRole } })
    .json<SwitchRoleResponse>();
};
