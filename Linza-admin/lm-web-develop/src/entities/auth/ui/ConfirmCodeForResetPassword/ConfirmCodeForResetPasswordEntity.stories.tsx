import { StoryObj } from "@storybook/react";

import ConfirmCodeForResetPasswordEntity from "./index";

export const Default: StoryObj<typeof ConfirmCodeForResetPasswordEntity> = {
  args: {
    loginType: "email",
  },
};

export default {
  title: "Entities/ConfirmCodeForResetPassword",
  component: ConfirmCodeForResetPasswordEntity,
};
