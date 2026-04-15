import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  addTeamMembers,
  createTeam,
  deleteTeam,
  getTeam,
  getTeamMembers,
  getTeams,
  removeTeamMember,
  updateTeam,
} from "./requests";

export const useTeamsQuery = () =>
  useQuery({ queryKey: ["teams"], queryFn: getTeams });

export const useTeamQuery = (id: number) =>
  useQuery({ queryKey: ["team", id], queryFn: () => getTeam(id) });

export const useTeamMembersQuery = (teamId: number) =>
  useQuery({
    queryKey: ["team-members", teamId],
    queryFn: () => getTeamMembers(teamId),
  });

export const useCreateTeamMutation = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (name: string) => createTeam(name),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["teams"] }),
  });
};

export const useUpdateTeamMutation = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, name }: { id: number; name: string }) =>
      updateTeam(id, name),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["teams"] }),
  });
};

export const useDeleteTeamMutation = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => deleteTeam(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["teams"] }),
  });
};

export const useAddTeamMembersMutation = (teamId: number) => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (userIds: number[]) => addTeamMembers(teamId, userIds),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: ["team-members", teamId] }),
  });
};

export const useRemoveTeamMemberMutation = (teamId: number) => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (userId: number) => removeTeamMember(teamId, userId),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: ["team-members", teamId] }),
  });
};
