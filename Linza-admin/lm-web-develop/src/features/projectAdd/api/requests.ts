import { HTTPError } from "ky";

import { projectSchema } from "@/entities/projects";
import { api } from "@/shared/api";

import { newProjectErrors } from "../models/response";

export function addProject({ name }: { name: string }) {
  return api
    .post("projects", { json: { name } })
    .json()
    .then(projectSchema.parse)
    .catch(async (error) => {
      if (error instanceof HTTPError && error.response.status === 400) {
        const err = await error.response.json().then(newProjectErrors.parse);
        return Promise.reject({ status: error.response.status, errors: err });
      } else {
        return Promise.reject({
          status: error.response.status,
          errors: { serverError: "server-error" },
        });
      }
    });
}
