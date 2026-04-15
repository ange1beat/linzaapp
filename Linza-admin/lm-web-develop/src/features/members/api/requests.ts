import { HTTPError } from "ky";

import { editMemberPasswordErrors } from "@/features/members/models/responses";
import { api } from "@/shared/api";

export function updateMemberPassword(data: {
  newPassword: string;
  memberId: string;
}) {
  return api
    .put(`users/${data.memberId}/password`, {
      json: { newPassword: data.newPassword },
    })
    .json()
    .catch(async (err) => {
      if (err instanceof HTTPError && err.response.status === 400) {
        const error = await err.response
          .json()
          .then(editMemberPasswordErrors.parse);
        return Promise.reject({
          status: err.response.status,
          errors: error.errors,
        });
      } else {
        return Promise.reject({});
      }
    });
}
