import env from "../../config/env";

export const authErr = {
  url: `${env.API_URL}/auth`,
  method: "POST",
  status: 401,
  response: {},
  delay: 1000,
};

export const auth = {
  url: `${env.API_URL}/auth`,
  method: "POST",
  status: 200,
  response: {
    user: {
      id: "some_user_id",
      email: "test@mail.com",
      phoneNumber: "88005553535",
    },
    stateToken: "some_state_token",
  },
  delay: 1000,
};

export const authByOtpErr = {
  url: `${env.API_URL}/auth/otp`,
  method: "POST",
  status: 400,
  response: {},
  delay: 2000,
};

export const sendOtpByEmail = {
  url: `${env.API_URL}/auth/otp/challenge/email`,
  method: "POST",
  status: 200,
  response: {
    otpId: "some_otp_id",
  },
  delay: 1000,
};

export const sendOtpBySms = {
  url: `${env.API_URL}/auth/otp/challenge/sms`,
  method: "POST",
  status: 200,
  response: {
    otpId: "some_otp_id",
  },
  delay: 1000,
};

export const revokeToken = {
  url: `${env.API_URL}/auth/tokens/revoke`,
  method: "POST",
  status: 204,
  response: {},
  delay: 1000,
};

export const getPasswordRecoveryToken = {
  url: `${env.API_URL}/auth/recovery/password/challenge`,
  method: "POST",
  status: 200,
  response: {
    stateToken: "some_state_token",
  },
  delay: 1000,
};

export const resetPassword = {
  url: `${env.API_URL}/auth/recovery/password`,
  method: "POST",
  status: 200,
  response: {},
  delay: 1000,
};
