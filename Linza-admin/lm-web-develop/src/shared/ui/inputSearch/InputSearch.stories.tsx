import type { Meta, StoryObj } from "@storybook/react";

import InputSearch from "./index";

const meta: Meta<typeof InputSearch> = {
  component: InputSearch,
  title: "shared/InputSearch",
  argTypes: {
    size: {
      options: ["xl", "l", "m", "s"],
      control: { type: "radio" },
    },
  },
};

export default meta;
type Story = StoryObj<typeof InputSearch>;

export const Default: Story = {
  args: {
    placeholder: "Search",
  },
};

export const WithError: Story = {
  args: {
    isError: true,
    errorMessage: "Error!",
  },
};
