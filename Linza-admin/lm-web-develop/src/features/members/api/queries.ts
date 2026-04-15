import { useMutation } from "@tanstack/react-query";

import { updateMemberPassword } from "./requests";

export function useUpdateMemberPassword() {
  return useMutation({
    mutationFn: updateMemberPassword,
  });
}
