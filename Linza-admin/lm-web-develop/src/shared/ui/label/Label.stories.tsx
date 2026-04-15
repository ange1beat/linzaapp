import { StoryObj } from "@storybook/react";

import Label from "./index";

export const Default: StoryObj<typeof Label> = {
  args: {
    theme: "normal" || "info" || "warning" || "danger",
    children: "It's awesome label",
  },
};

export default {
  title: "Shared/Label",
  component: Label,
};
