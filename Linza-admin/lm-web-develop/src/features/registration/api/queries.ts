import { useMutation, useQuery } from "@tanstack/react-query";

import { createAccount, checkInvitationId } from "./requests";

export function useCreateAccountMutation() {
  return useMutation({
    mutationFn: createAccount,
  });
}
export function useInvitationIdQuery(invitationId: string) {
  const { isPending, isError } = useQuery({
    queryKey: ["invitationId", invitationId],
    queryFn: () => checkInvitationId(invitationId),
    enabled: !!invitationId,
  });
  return { isPending, isError };
}
