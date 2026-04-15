import { HTTPError } from "ky";

import { api } from "@/shared/api";
import { flatErrors } from "@/shared/lib/errors";

import { updateProjectNameResponse } from "../models/response";

export function updateProjectName(project: { id: string; name: string }) {
  return api
    .put(`projects/${project.id}/name`, { json: { name: project.name } })
    .catch(async (err) => {
      if (err instanceof HTTPError && err.response.status === 400) {
        const response = await err.response
          .json()
          .then(updateProjectNameResponse.parse);
        return Promise.reject({
          status: err.response.status,
          errors: flatErrors(response.errors),
        });
      }
      if (err instanceof HTTPError && err.response.status === 409) {
        return Promise.reject({
          status: err.response.status,
        });
      } else {
        return Promise.reject({});
      }
    });
}
