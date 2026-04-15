import { Meta, StoryObj } from "@storybook/react";

import ChangeEmail from "./index";

const meta: Meta<typeof ChangeEmail> = {
  component: ChangeEmail,
  title: "Features/userChangeEmail/ChangeEmail",
  argTypes: {},
};

export default meta;

type Story = StoryObj<typeof ChangeEmail>;

export const Default: Story = {
  argTypes: {},
  args: {},
};
