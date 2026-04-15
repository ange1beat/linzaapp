import { HTTPError } from "ky";

import { api } from "@/shared/api";

import { verifyOTPResponse, setPasswordErrors } from "../models/response";

export function recoveryPWDByEmail({
  email,
  locale,
}: {
  email: string;
  locale: string;
}) {
  return api
    .post("auth/recovery/password/challenge/email", {
      json: { email, language: locale },
    })
    .catch(async (err) => {
      if (err instanceof HTTPError && err.response.status === 500) {
        return Promise.reject({ status: err.response.status });
      } else {
        return Promise.reject({});
      }
    });
}

export function recoveryPWDBySMS({
  phoneNumber,
  locale,
}: {
  phoneNumber: string;
  locale: string;
}) {
  return api
    .post("auth/recovery/password/challenge/sms", {
      json: { phoneNumber, language: locale },
    })
    .catch(async (err) => {
      if (err instanceof HTTPError && err.response.status === 500) {
        return Promise.reject({ status: err.response.status });
      } else {
        return Promise.reject({});
      }
    });
}

export function recoveryVerify({
  login,
  recoveryCode,
}: {
  login: string;
  recoveryCode: string;
}) {
  return api
    .post("auth/recovery/password/verify", {
      json: { login, recoveryCode },
    })
    .json()
    .then(verifyOTPResponse.parse)
    .catch((err) => {
      return Promise.reject({ status: err.response.status });
    });
}

export function setPassword(data: {
  recoveryToken: string;
  newPassword: string;
}) {
  return api
    .post("auth/recovery/password/reset", { json: data })
    .json()
    .catch(async (error) => {
      if (error instanceof HTTPError) {
        const status = error.response.status;
        if (status === 400) {
          const err = await error.response.json().then(setPasswordErrors.parse);
          return Promise.reject({ status, errors: err.errors });
        } else {
          return Promise.reject({ status });
        }
      } else {
        return Promise.reject({});
      }
    });
}
