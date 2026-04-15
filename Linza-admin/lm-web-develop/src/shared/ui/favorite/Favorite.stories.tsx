import { Meta, StoryObj } from "@storybook/react";

import Favorite from "./index";

const meta: Meta<typeof Favorite> = {
  component: Favorite,
  title: "Shared/Favorite",
  argTypes: {},
};

export default meta;

type Story = StoryObj<typeof Favorite>;

export const Default: Story = {
  argTypes: {},
  args: {
    isSelected: false,
  },
};

export const Selected: Story = {
  argTypes: {},
  args: {
    isSelected: true,
  },
};
