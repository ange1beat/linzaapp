import { api } from "@/shared/api";

import type { ITeam, ITeamMember } from "../models/models";

export const getTeams = (): Promise<ITeam[]> =>
  api.get("teams/").json<ITeam[]>();

export const getTeam = (id: number): Promise<ITeam> =>
  api.get(`teams/${id}`).json<ITeam>();

export const createTeam = (name: string): Promise<ITeam> =>
  api.post("teams/", { json: { name } }).json<ITeam>();

export const updateTeam = (id: number, name: string): Promise<ITeam> =>
  api.patch(`teams/${id}`, { json: { name } }).json<ITeam>();

export const deleteTeam = (id: number): Promise<void> =>
  api.delete(`teams/${id}`).then(() => undefined);

export const getTeamMembers = (teamId: number): Promise<ITeamMember[]> =>
  api.get(`teams/${teamId}/members`).json<ITeamMember[]>();

export const addTeamMembers = (
  teamId: number,
  userIds: number[],
): Promise<{ updated: number }> =>
  api
    .post(`teams/${teamId}/members`, { json: { user_ids: userIds } })
    .json<{ updated: number }>();

export const removeTeamMember = (
  teamId: number,
  userId: number,
): Promise<void> =>
  api.delete(`teams/${teamId}/members/${userId}`).then(() => undefined);
