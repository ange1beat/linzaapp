import { Meta, StoryObj } from "@storybook/react";

import KeyField from "./index";

const meta: Meta<typeof KeyField> = {
  component: KeyField,
  title: "shared/KeyField",
  argTypes: {},
};

export default meta;

type Story = StoryObj<typeof KeyField>;

export const Default: Story = {
  args: {},
};

export const Error: Story = {
  args: {
    isError: true,
    errorMessage: "The code is incorrect",
  },
};

export const Disabled: Story = {
  args: {
    disabled: true,
  },
};

export const WithClassName: Story = {
  args: {
    className: "my-class",
  },
};
