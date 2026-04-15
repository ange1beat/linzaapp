import { useMutation } from "@tanstack/react-query";

import { changePasswordRequest } from "./requests";

export function useChangePasswordMutation() {
  return useMutation({
    mutationFn: changePasswordRequest,
  });
}
