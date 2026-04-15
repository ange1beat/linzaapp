import { Meta, StoryObj } from "@storybook/react";

import ResetPasswordFeature from "./index";

const meta: Meta<typeof ResetPasswordFeature> = {
  component: ResetPasswordFeature,
  title: "Features/pwdRecovery/S  etPassword",
  argTypes: {},
};

export default meta;

type Story = StoryObj<typeof ResetPasswordFeature>;

export const Default: Story = {
  args: {},
};
