import { useMutation, useQuery } from "@tanstack/react-query";

import { deleteFolder, getFolders } from "@/entities/folders/api/requests";
import { queryClient } from "@/shared/api";
import { PAGE_SIZE } from "@/shared/config";

export function useFoldersQuery(
  projectId: string,
  pageNumber = 1,
  pageSize = PAGE_SIZE,
  name?: string,
) {
  const { isPending, data } = useQuery({
    queryKey: ["folders", { name, pageSize, pageNumber, projectId }],
    queryFn: () => getFolders({ name, pageNumber, pageSize, projectId }),
  });
  return {
    isPending,
    folders: data?.folders ?? [],
    total: data?.total ?? 0,
  };
}

export function useDeleteFolderMutation() {
  return useMutation({
    mutationFn: deleteFolder,
    onSuccess: () =>
      queryClient.invalidateQueries({
        queryKey: ["folders"],
      }),
  });
}
