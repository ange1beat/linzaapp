import { StoryObj } from "@storybook/react";

import UpdatePasswordEntity from "./index";

export const Default: StoryObj<typeof UpdatePasswordEntity> = {
  args: {
    errors: { currentPassword: "", newPassword: "", confirmPassword: "" },
    isLoad: false,
    onSubmit: () => {},
    onChange: () => {},
  },
};

export default {
  title: "Entities/UpdatePassword",
  component: UpdatePasswordEntity,
};
