import { StoryObj } from "@storybook/react";

import { authErr } from "@/shared/storybook/mocks/authAPI";

import LoginFeature from "./index";

export const Default: StoryObj<typeof LoginFeature> = {
  args: {},
};

export default {
  title: "Features/LoginFeature",
  component: LoginFeature,
  parameters: {
    mockData: [authErr],
  },
};
