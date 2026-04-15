import { useMutation } from "@tanstack/react-query";

import { queryClient } from "@/shared/api";

import { addProjectFav, delProjectFav } from "./requests";

export function useAddProjectFavMutation() {
  return useMutation({
    mutationFn: addProjectFav,
    onSuccess: () =>
      queryClient.invalidateQueries({
        queryKey: ["projects", "list", "favorite"],
      }),
  });
}

export function useDelProjectFavMutation() {
  return useMutation({
    mutationFn: delProjectFav,
    onSuccess: () =>
      queryClient.invalidateQueries({
        queryKey: ["projects", "list", "favorite"],
      }),
  });
}
