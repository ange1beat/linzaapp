import { Meta, StoryObj } from "@storybook/react";

import ChangePhone from "./index";

const meta: Meta<typeof ChangePhone> = {
  component: ChangePhone,
  title: "Features/userChangePhone/ChangePhone",
  argTypes: {},
};

export default meta;

type Story = StoryObj<typeof ChangePhone>;

export const Default: Story = {
  argTypes: {},
  args: {},
};
