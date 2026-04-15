import { HTTPError } from "ky";

import { api } from "@/shared/api";

import { telegramError } from "../models/responses";

export async function updateUserTelegram(telegramName: string) {
  return api
    .put("users/me/telegram", { json: { username: telegramName.slice(1) } })
    .catch(async (error) => {
      if (error instanceof HTTPError) {
        const status = error.response.status;
        if (error.response.status === 400) {
          const err = await error.response.json().then(telegramError.parse);
          return Promise.reject({ status, errors: err.errors });
        } else {
          return Promise.reject();
        }
      }
    });
}
