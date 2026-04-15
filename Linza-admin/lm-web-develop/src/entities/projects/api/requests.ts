import { HTTPError } from "ky";

import { projectsOfMemberSchema } from "@/entities/projects/models";
import { api } from "@/shared/api";
import { PAGE_SIZE } from "@/shared/config";
import { newAvatarErrors } from "@/shared/models/avatar";

import {
  projectSchema,
  favoriteProjectsResponse,
  projectsResponse,
} from "../models";

export function getProjects(
  search?: string,
  pageSize = PAGE_SIZE,
  pageNumber = 1,
) {
  const searchParams = new URLSearchParams();
  search && searchParams.set("name", search);
  searchParams.set("PageSize", pageSize.toString());
  searchParams.set("PageNumber", pageNumber.toString());
  return api
    .get("projects", { searchParams })
    .json()
    .then(projectsResponse.parse);
}

export function getFavoritesProjects() {
  return api
    .get("projects/favorites")
    .json()
    .then(favoriteProjectsResponse.parse);
}

export function getProject(projectId: string) {
  return api.get(`projects/${projectId}`).json().then(projectSchema.parse);
}

export function getProjectsOfMember(userId: string) {
  return api
    .get(`projects/membership/${userId}`)
    .json()
    .then(projectsOfMemberSchema.parse);
}

export function manageProjectsMembership(data: {
  userId: string;
  operation: string;
  projectIds: string[];
}) {
  const { userId, projectIds, operation } = data;
  return api
    .patch(`projects/membership/${userId}`, { json: { operation, projectIds } })
    .json()
    .catch(() => Promise.reject({}));
}

export function updateProjectAvatar(data: {
  projectId: string;
  avatar: FormData;
}) {
  return api
    .put(`projects/${data.projectId}/avatar`, {
      body: data.avatar,
    })
    .catch(async (error) => {
      if (error instanceof HTTPError && error.response.status === 400) {
        const err = await error.response.json().then(newAvatarErrors.parse);
        return Promise.reject({ status: error.response.status, errors: err });
      } else {
        return Promise.reject({});
      }
    });
}
