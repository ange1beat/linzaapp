import { useMutation, useQuery } from "@tanstack/react-query";

import { queryClient } from "@/shared/api";
import { PAGE_SIZE, USER_ROLES } from "@/shared/config";

import {
  addMembersToProject,
  deleteMemberFromProject,
  getMembersInfo,
  getMembersInProject,
  getSelectedMember,
} from "./requests";

export function useMembersQuery(
  search: string,
  pageSize = PAGE_SIZE,
  pageNumber = 1,
  userIds?: string[],
) {
  const { isPending, data } = useQuery({
    queryKey: ["members", { search, pageSize, pageNumber, userIds }],
    queryFn: () =>
      getMembersInfo({
        searchTerm: search,
        pageNumber,
        pageSize,
        includeIds: userIds,
      }),
  });
  return {
    isPending,
    members: data?.users ?? [],
    total: data?.total ?? 0,
  };
}

export function useGetProjectMembersQuery(projectId: string) {
  const { isPending, data } = useQuery({
    queryKey: ["projects", "detail", { projectId }, "members"],
    queryFn: () => getMembersInProject(projectId),
    enabled: !!projectId,
  });

  return {
    isPending,
    membersIds: data?.userIds ?? [],
    total: data?.userIds.length ?? 0,
  };
}

export function useGetMemberQuery(memberId: string) {
  const { isPending, data } = useQuery({
    queryKey: ["member", { memberId }],
    queryFn: () => getSelectedMember(memberId),
  });
  return {
    isPending,
    selectedMember: data ?? {
      id: "",
      firstName: "",
      lastName: "",
      email: "",
      phoneNumber: "",
      telegramUsername: "",
      roles: [USER_ROLES.User],
      avatarUrl: "",
    },
  };
}

export function useAddMembersToProjectMutation(projectId: string) {
  return useMutation({
    mutationFn: addMembersToProject,
    onSuccess: () =>
      queryClient.invalidateQueries({
        queryKey: ["projects", "detail", { projectId }, "members"],
      }),
  });
}

export function useDeleteMemberFromProjectMutation(projectId: string) {
  return useMutation({
    mutationFn: deleteMemberFromProject,
    onSuccess: () =>
      queryClient.invalidateQueries({
        queryKey: ["projects", "detail", { projectId }, "members"],
      }),
  });
}
