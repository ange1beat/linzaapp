import type { StoryObj } from "@storybook/react";

import {
  auth,
  authByOtpErr,
  sendOtpByEmail,
  sendOtpBySms,
} from "../../shared/storybook/mocks/authAPI";

import LoginPage from "./index";

export const Default: StoryObj<typeof LoginPage> = {};

export default {
  title: "Pages/LoginPage",
  component: LoginPage,
  parameters: {
    mockData: [auth, authByOtpErr, sendOtpBySms, sendOtpByEmail],
  },
};
