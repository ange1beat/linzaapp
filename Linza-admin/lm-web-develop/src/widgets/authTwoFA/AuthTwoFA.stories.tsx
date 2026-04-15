import { StoryObj } from "@storybook/react";

import {
  authByOtpErr,
  sendOtpByEmail,
  sendOtpBySms,
} from "@/shared/storybook/mocks/authAPI";

import AuthTwoFA from "./index";

export const Default: StoryObj<typeof AuthTwoFA> = {
  args: {
    isLoading: false,
  },
};

export default {
  title: "Widgets/AuthTwoFA",
  component: AuthTwoFA,
  parameters: {
    mockData: [sendOtpBySms, sendOtpByEmail, authByOtpErr],
  },
};
