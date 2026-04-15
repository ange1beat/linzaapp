import { StoryObj } from "@storybook/react";

import Spin from "./index";

export const Default: StoryObj<typeof Spin> = {
  args: {
    size: "m",
  },
};

export default {
  title: "Shared/Spin",
  component: Spin,
};
