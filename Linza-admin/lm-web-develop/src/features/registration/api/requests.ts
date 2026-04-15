import { HTTPError } from "ky";

import { api } from "@/shared/api";

import { createUserErrors } from "../models/responses";

export function createAccount(data: {
  invitationId: string;
  firstName: string;
  lastName: string;
  password: string;
}) {
  return api
    .post("users/registration", { json: data })
    .json()
    .catch(async (error: HTTPError) => {
      const status = error.response.status;
      if (status === 400) {
        const err = await error.response.json().then(createUserErrors.parse);
        return Promise.reject({ status, errors: err.errors });
      }
      if (status === 403) {
        return Promise.reject({ status });
      }
    });
}

export function checkInvitationId(id: string) {
  return api.get(`users/invitations/${id}`);
}
