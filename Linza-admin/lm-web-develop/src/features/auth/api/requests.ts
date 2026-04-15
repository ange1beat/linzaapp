import { HTTPError } from "ky";
import { z } from "zod";

import { api } from "@/shared/api";

import {
  loginResponse,
  sendOtpCodeResponse,
  verificationOtpResponse,
} from "../models/responses";

export function authorizeUser(data: {
  login: string;
  password: string;
}): Promise<z.infer<typeof loginResponse>> {
  return api
    .post("auth", {
      json: data,
    })
    .json()
    .then(loginResponse.parse)
    .catch(async (err) => {
      if (err instanceof HTTPError) {
        const retryAfterValue = err.response.headers.get("Retry-After");
        const status = err.response.status;
        if (status === 401 && retryAfterValue) {
          return Promise.reject({
            status: status,
            retryAfterValue: retryAfterValue,
          });
        }
        if (status === 500) {
          return Promise.reject({ status: status });
        }
      }
      return Promise.reject({});
    });
}

export function sendConfirmCode(data: {
  stateToken: string;
  passcode: string;
}) {
  return api
    .post("auth/factors/otp/verify", { json: data })
    .json()
    .then(sendOtpCodeResponse.parse)
    .catch(async (error) => {
      if (error instanceof HTTPError && error.response.status === 401) {
        return Promise.reject({ status: error.response.status });
      } else {
        return Promise.reject({});
      }
    });
}

export function sendVerificationOtpResponse(data: {
  otpId: string;
  otpValue: string;
}): Promise<z.infer<typeof verificationOtpResponse>> {
  return api
    .post("auth/recovery/password/challenge", { json: data })
    .json()
    .then(verificationOtpResponse.parse);
}
