import { Meta, StoryObj } from "@storybook/react";

import VerifyOTP from "./index";

const meta: Meta<typeof VerifyOTP> = {
  component: VerifyOTP,
  title: "Features/pwdRecovery/VerifyOTP",
  argTypes: {},
};

export default meta;

type Story = StoryObj<typeof VerifyOTP>;

export const Default: Story = {
  args: {
    login: "somemail@mail.ru",
    children: <button>request code again</button>,
    loginType: "email",
  },
};
