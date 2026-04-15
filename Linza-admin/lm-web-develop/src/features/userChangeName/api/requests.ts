import { HTTPError } from "ky";

import { updateUserNameResponse } from "@/features/userChangeName/models/response";
import { api } from "@/shared/api";
import { flatErrors } from "@/shared/lib/errors";

export function updateUserName(user: { firstName: string; lastName: string }) {
  return api
    .put(`users/me/name`, { json: { ...user } })
    .json()
    .catch(async (err) => {
      if (err instanceof HTTPError && err.response.status === 400) {
        const response = await err.response
          .json()
          .then(updateUserNameResponse.parse);
        return Promise.reject({
          status: err.response.status,
          errors: flatErrors(response.errors),
        });
      } else {
        return Promise.reject({});
      }
    });
}
