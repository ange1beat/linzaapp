import { StoryObj } from "@storybook/react";

import PhoneNumberField from "./index";

export default {
  component: PhoneNumberField,
  title: "shared/PhoneNumberField",
  args: {},
};

type Story = StoryObj<typeof PhoneNumberField>;

export const Default: Story = {
  args: {},
};
