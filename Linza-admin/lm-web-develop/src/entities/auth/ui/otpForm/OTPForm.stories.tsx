import { Meta, StoryObj } from "@storybook/react";

import OTPForm from "./index";

const meta: Meta<typeof OTPForm> = {
  component: OTPForm,
  title: "Entities/OTPForm",
  argTypes: {},
};

export default meta;

type Story = StoryObj<typeof OTPForm>;

export const Default: Story = {
  argTypes: {},
  args: {
    email: "example@mail.com",
    onSubmit: () => Promise.resolve(),
    children: <button>Request again</button>,
  },
};
