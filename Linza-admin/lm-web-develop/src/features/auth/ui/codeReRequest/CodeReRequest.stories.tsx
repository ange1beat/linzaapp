import { StoryObj } from "@storybook/react";

import { sendOtpByEmail, sendOtpBySms } from "@/shared/storybook/mocks/authAPI";

import CodeReRequest from "./index";

export const Default: StoryObj<typeof CodeReRequest> = {
  args: {
    timer: 5,
    loginType: "email",
  },
};

export default {
  title: "Features/CodeReRequest",
  component: CodeReRequest,
  parameters: {
    mockData: [sendOtpByEmail, sendOtpBySms],
  },
};
