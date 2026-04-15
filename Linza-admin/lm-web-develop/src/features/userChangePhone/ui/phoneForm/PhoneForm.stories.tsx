import { Meta, StoryObj } from "@storybook/react";

import PhoneForm from "./index";

const meta: Meta<typeof PhoneForm> = {
  component: PhoneForm,
  title: "Features/userChangePhone/PhoneForm",
  argTypes: {},
};

export default meta;

type Story = StoryObj<typeof PhoneForm>;

export const Default: Story = {
  argTypes: {},
  args: {},
};
