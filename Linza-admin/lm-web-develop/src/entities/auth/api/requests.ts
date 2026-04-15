import { HTTPError } from "ky";

import { api } from "@/shared/api";

export function sendOtpByEmail(data: { stateToken: string; locale: string }) {
  const { stateToken, locale } = data;
  return api
    .post("auth/factors/otp/challenge/email", {
      json: { stateToken, language: locale },
    })
    .catch(async (err) => {
      if (err instanceof HTTPError && err.response.status === 500) {
        return Promise.reject({ status: err.response.status });
      } else {
        return Promise.reject({});
      }
    });
}

export function sendOtpBySMS(data: { stateToken: string; locale: string }) {
  const { stateToken, locale } = data;
  return api
    .post("auth/factors/otp/challenge/sms", {
      json: { stateToken, language: locale },
    })
    .catch(async (err) => {
      if (err instanceof HTTPError && err.response.status === 500) {
        return Promise.reject({ status: err.response.status });
      } else {
        return Promise.reject({});
      }
    });
}
