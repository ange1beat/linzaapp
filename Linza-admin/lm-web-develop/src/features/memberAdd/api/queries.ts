import { useMutation } from "@tanstack/react-query";

import { createMember } from "@/features/memberAdd/api/requests";

export function useCreateMember() {
  return useMutation({
    mutationFn: createMember,
  });
}
