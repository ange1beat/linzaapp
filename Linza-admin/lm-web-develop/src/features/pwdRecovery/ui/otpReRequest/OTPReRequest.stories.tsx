import { StoryObj } from "@storybook/react";

import OTPReRequest from "./index";

export const Default: StoryObj<typeof OTPReRequest> = {
  args: {
    timer: 5,
    login: "test@mail.com",
    loginType: "email",
  },
};

export default {
  title: "Features/pwdRecovery/OTPReRequest",
  component: OTPReRequest,
};
