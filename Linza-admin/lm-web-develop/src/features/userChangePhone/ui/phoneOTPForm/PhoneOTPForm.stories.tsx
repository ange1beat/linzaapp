import { Meta, StoryObj } from "@storybook/react";

import PhoneOTPForm from "./index";

const meta: Meta<typeof PhoneOTPForm> = {
  component: PhoneOTPForm,
  title: "Features/userChangePhone/PhoneOTPForm",
  argTypes: {},
};

export default meta;

type Story = StoryObj<typeof PhoneOTPForm>;

export const Default: Story = {
  argTypes: {},
  args: {
    phone: "+78005553535",
  },
};
