import { HTTPError } from "ky";
import { z } from "zod";

import { api } from "@/shared/api";

import {
  memberSchema,
  membersInProjectSchema,
  membersSchema,
} from "../models/responses";

export function getMembersInfo(data: {
  searchTerm?: string;
  pageNumber?: number;
  pageSize?: number;
  includeIds?: string[];
  excludeIds?: string[];
}): Promise<z.infer<typeof membersSchema>> {
  return api.post("users/search", { json: data }).json();
}

export function getSelectedMember(
  userId: string,
): Promise<z.infer<typeof memberSchema>> {
  return api.get(`users/${userId}`).json().then(memberSchema.parse);
}

export function getMembersInProject(
  projectId: string,
): Promise<z.infer<typeof membersInProjectSchema>> {
  return api
    .get(`projects/${projectId}/members`)
    .json()
    .then(membersInProjectSchema.parse);
}

export function addMembersToProject(data: {
  projectId: string;
  userIds: string[];
}) {
  return api
    .post(`projects/${data.projectId}/members`, {
      json: { userIds: data.userIds },
    })
    .json()
    .catch(async (err) => {
      if (err instanceof HTTPError && err.response.status === 400) {
        return Promise.reject({ status: 400 });
      } else {
        return Promise.reject({});
      }
    });
}

export function deleteMemberFromProject(data: {
  projectId: string;
  userId: string;
}) {
  const { projectId, userId } = data;
  return api.delete(`projects/${projectId}/members/${userId}`);
}
