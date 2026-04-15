import { useMutation, useQuery } from "@tanstack/react-query";

import { queryClient } from "@/shared/api";
import { PAGE_SIZE } from "@/shared/config/constants";

import {
  getProjects,
  getProject,
  getFavoritesProjects,
  getProjectsOfMember,
  manageProjectsMembership,
  updateProjectAvatar,
} from "./requests";

export function useProjectsQuery(
  search?: string,
  pageNumber = 1,
  pageSize = PAGE_SIZE,
) {
  const { data, isPending } = useQuery({
    queryKey: ["projects", "list", { search, pageSize, pageNumber }],
    queryFn: () => getProjects(search, pageSize, pageNumber),
  });
  return {
    projects: data?.projects ?? [],
    total: data?.total ?? 0,
    isPending,
  };
}

export function useFavProjectsQuery() {
  const { data, isPending } = useQuery({
    queryKey: ["projects", "list", "favorite"],
    queryFn: getFavoritesProjects,
  });
  return {
    projects: data?.favorites ?? [],
    isPending,
  };
}

export function useProjectQuery(projectId: string) {
  const { isPending, data } = useQuery({
    queryKey: ["projects", "detail", projectId],
    queryFn: () => getProject(projectId),
  });
  return {
    isPending,
    project: data ?? {
      id: "",
      name: "",
      tenantId: "",
      createdBy: "",
      createdAt: "",
      avatarUrl: "",
    },
  };
}

export function useProjectsOfMemberQuery(memberId: string) {
  const { data, isPending } = useQuery({
    queryKey: ["members", memberId, "projects"],
    queryFn: () => getProjectsOfMember(memberId),
  });

  return {
    isPending,
    projects: data ?? {
      projectIds: [],
      userId: "",
    },
  };
}

export function useManageProjectsMembership(memberId: string) {
  return useMutation({
    mutationFn: manageProjectsMembership,
    onSuccess: () =>
      queryClient.invalidateQueries({
        queryKey: ["members", memberId, "projects"],
      }),
  });
}

export function useProjectAvatarMutation() {
  return useMutation({
    mutationFn: updateProjectAvatar,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["projects"] }),
  });
}
