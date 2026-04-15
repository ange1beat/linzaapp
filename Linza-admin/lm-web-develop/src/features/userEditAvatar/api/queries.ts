import { useMutation } from "@tanstack/react-query";

import { queryClient } from "@/shared/api";

import { uploadAvatarUser } from "./requests";

export function useUploadAvatar() {
  return useMutation({
    mutationFn: uploadAvatarUser,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["user"] });
    },
  });
}
