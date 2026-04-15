import type { Meta, StoryObj } from "@storybook/react";

import Variants from "./Variants";

import Text from "./index";

const meta: Meta<typeof Text> = {
  component: Text,
  title: "shared/Text",
  argTypes: {},
};

export default meta;
type Story = StoryObj<typeof Text>;

export const Default: Story = {
  args: {
    children: Variants(),
  },
};
