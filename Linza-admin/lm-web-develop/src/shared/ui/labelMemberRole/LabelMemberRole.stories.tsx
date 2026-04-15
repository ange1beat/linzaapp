import { StoryObj } from "@storybook/react";

import LabelMemberRole from "./index";

export const Default: StoryObj<typeof LabelMemberRole> = {
  args: {
    role: "User" || "Supervisor",
  },
};

export default {
  title: "Shared/LabelMemberRole",
  component: LabelMemberRole,
};
