import { StoryObj } from "@storybook/react";

import Skeleton from "./index";

export const Default: StoryObj<typeof Skeleton> = {
  args: {
    isLoad: true,
    height: 20,
  },
};

export default {
  title: "Shared/Skeleton",
  component: Skeleton,
};
