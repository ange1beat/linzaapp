import { Meta, StoryObj } from "@storybook/react";

import LoginInput from "./index";

const meta: Meta<typeof LoginInput> = {
  component: LoginInput,
  title: "Features/pwdRecovery/LoginInput",
  argTypes: {},
};

export default meta;

type Story = StoryObj<typeof LoginInput>;

export const Default: Story = {
  args: {},
};
