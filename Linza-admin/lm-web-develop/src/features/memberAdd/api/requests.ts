import { HTTPError } from "ky";

import { addMemberRequestErrorsSchema } from "@/features/memberAdd/models/responses";
import { api } from "@/shared/api";

export function createMember({
  email,
  language,
}: {
  email: string;
  language: string;
}) {
  return api
    .post("users/invitations", {
      json: { email: email.toLowerCase(), language },
    })
    .json()
    .catch(async (error) => {
      const status = error.response.status;
      if (error instanceof HTTPError && status === 400) {
        const err = await error.response
          .json()
          .then(addMemberRequestErrorsSchema.parse);
        return Promise.reject({ status: 400, errors: err.errors });
      } else {
        return Promise.reject({ status: status });
      }
    });
}
