import { StoryObj } from "@storybook/react";

import Loader from "./index";

export const Default: StoryObj<typeof Loader> = {
  args: {
    size: "m",
  },
};

export default {
  title: "Shared/Loader",
  component: Loader,
};
