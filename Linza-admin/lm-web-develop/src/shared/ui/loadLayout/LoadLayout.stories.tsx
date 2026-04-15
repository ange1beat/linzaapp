import type { StoryObj } from "@storybook/react";

import LoadLayout from "./index";

export const Default: StoryObj<typeof LoadLayout> = {
  args: {
    isLoad: true,
  },
};

export default {
  title: "Shared/LoadLayout",
  component: LoadLayout,
};
