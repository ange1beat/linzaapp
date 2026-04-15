import { useMutation } from "@tanstack/react-query";

import { revokeToken } from "./token";

export function useRevokeTokenMutation() {
  return useMutation({
    mutationFn: revokeToken,
  });
}
