import type { StoryObj } from "@storybook/react";

import {
  getPasswordRecoveryToken,
  resetPassword,
  sendOtpByEmail,
  sendOtpBySms,
} from "@/shared/storybook/mocks/authAPI";

import ResetPasswordPage from "./index";

export const Default: StoryObj<typeof ResetPasswordPage> = {};

export default {
  title: "Pages/ResetPasswordPage",
  component: ResetPasswordPage,
  parameters: {
    mockData: [
      sendOtpBySms,
      sendOtpByEmail,
      getPasswordRecoveryToken,
      resetPassword,
    ],
  },
};
