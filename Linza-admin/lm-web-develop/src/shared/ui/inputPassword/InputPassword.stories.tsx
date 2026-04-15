import type { Meta, StoryObj } from "@storybook/react";

import InputPassword from "./index";

const meta: Meta<typeof InputPassword> = {
  component: InputPassword,
  title: "shared/InputPassword",
  argTypes: {
    size: {
      options: ["l", "s", "m", "xl"],
      control: { type: "radio" },
    },
  },
};

export default meta;
type Story = StoryObj<typeof InputPassword>;

export const Default: Story = {
  args: {
    placeholder: "text something",
  },
};

export const WithError: Story = {
  args: {
    isError: true,
    errorMessage: "Error!",
  },
};
