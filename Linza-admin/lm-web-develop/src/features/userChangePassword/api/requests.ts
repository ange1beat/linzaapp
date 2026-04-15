import { HTTPError } from "ky";

import { updateUserPasswordsErrors } from "@/features/userChangePassword/models/response";
import { api } from "@/shared/api";
import { flatErrors } from "@/shared/lib/errors";

export function changePasswordRequest(data: {
  currentPassword: string;
  newPassword: string;
}) {
  return api
    .put("users/me/password", { json: data })
    .json()
    .catch(async (error) => {
      if (error instanceof HTTPError && error.response.status === 400) {
        const response = await error.response
          .json()
          .then(updateUserPasswordsErrors.parse);
        return Promise.reject({
          status: error.response.status,
          errors: flatErrors(response.errors),
        });
      } else {
        return Promise.reject({});
      }
    });
}
