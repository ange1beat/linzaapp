import { Meta, StoryObj } from "@storybook/react";

import EmailOTPForm from "./index";

const meta: Meta<typeof EmailOTPForm> = {
  component: EmailOTPForm,
  title: "Features/userChangeEmail/EmailOTPForm",
  argTypes: {},
};

export default meta;

type Story = StoryObj<typeof EmailOTPForm>;

export const Default: Story = {
  argTypes: {},
  args: {
    email: "example@mail.com",
  },
};
