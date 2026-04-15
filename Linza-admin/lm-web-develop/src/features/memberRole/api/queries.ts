import { useMutation } from "@tanstack/react-query";

import { IMember } from "@/entities/members";
import { queryClient } from "@/shared/api";
import { USER_ROLES } from "@/shared/config";

import { changeMemberRole } from "./requests";

export function useMemberRoleMutation() {
  return useMutation({
    mutationFn: changeMemberRole,
    onSuccess: (response, props) => {
      const roles = [USER_ROLES.User];
      if (props.isSupervisor) {
        roles.push(USER_ROLES.Supervisor);
      }
      queryClient.setQueryData(
        ["member", { memberId: props.memberId }],
        (prevData: IMember) => ({
          ...prevData,
          roles,
        }),
      );
      queryClient.invalidateQueries({
        queryKey: ["members"],
      });
    },
  });
}
