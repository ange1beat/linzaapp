import { HTTPError } from "ky";
import { z } from "zod";

import { api } from "@/shared/api";

import {
  memberSchema,
  membersSchema,
} from "../models/responses";

export function getMembersInfo(data: {
  searchTerm?: string;
  pageNumber?: number;
  pageSize?: number;
  includeIds?: string[];
  excludeIds?: string[];
}): Promise<z.infer<typeof membersSchema>> {
  return api
    .post("users/search", { json: data })
    .json()
    .then(membersSchema.parse);
}

export function getSelectedMember(
  userId: string,
): Promise<z.output<typeof memberSchema>> {
  return api.get(`users/${userId}`).json().then(memberSchema.parse);
}

export function getMembersInProject(projectId: string) {
  // New backend returns array of member objects
  return api
    .get(`projects/${projectId}/members`)
    .json<{ id: number; user_id: number; role: string }[]>()
    .then((members) => ({
      userIds: members.map((m) => String(m.user_id)),
    }));
}

export function addMembersToProject(data: {
  projectId: string;
  userIds: string[];
}) {
  // Backend expects user_ids as numbers
  return api
    .post(`projects/${data.projectId}/members`, {
      json: { user_ids: data.userIds.map(Number), role: "viewer" },
    })
    .json()
    .catch(async (err) => {
      if (err instanceof HTTPError && err.response.status === 400) {
        return Promise.reject({ status: 400 });
      }
      return Promise.reject({});
    });
}

export function deleteMemberFromProject(data: {
  projectId: string;
  userId: string;
}) {
  const { projectId, userId } = data;
  return api.delete(`projects/${projectId}/members/${userId}`);
}
