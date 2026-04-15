import { StoryObj } from "@storybook/react";

import Checkbox from "./index";

export const Checked: StoryObj<typeof Checkbox> = {
  args: {
    checked: true,
    onChange: () => {},
  },
};

export const NotChecked: StoryObj<typeof Checkbox> = {
  args: {
    checked: false,
    onChange: () => {},
  },
};

export default {
  title: "Shared/Checkbox",
  component: Checkbox,
  argTypes: {
    size: {
      options: ["m", "l"],
      control: { type: "radio" },
    },
  },
};
