import { HTTPError } from "ky";

import { api } from "@/shared/api";

export function updateProjectName(project: { id: string; name: string }) {
  // Backend uses PATCH /projects/{id} with { name } body
  return api
    .patch(`projects/${project.id}`, { json: { name: project.name } })
    .catch(async (err) => {
      if (err instanceof HTTPError && err.response.status === 400) {
        return Promise.reject({ status: err.response.status });
      }
      if (err instanceof HTTPError && err.response.status === 409) {
        return Promise.reject({ status: err.response.status });
      }
      return Promise.reject({});
    });
}
