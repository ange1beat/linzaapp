import { HTTPError } from "ky";

import { api } from "@/shared/api";
import { newAvatarErrors } from "@/shared/models/avatar";

export async function uploadAvatarUser(data: FormData) {
  return api
    .put("users/me/avatar", { body: data })
    .json()
    .catch(async (error) => {
      if (error instanceof HTTPError) {
        const status = error.response.status;
        const err = await error.response.json().then(newAvatarErrors.parse);
        if (status === 400) {
          return Promise.reject({ status: status, errors: err });
        } else {
          return Promise.reject({});
        }
      }
    });
}
