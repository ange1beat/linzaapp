import { Meta, StoryObj } from "@storybook/react";

import InputConfirm from "./index";

const meta: Meta<typeof InputConfirm> = {
  component: InputConfirm,
  title: "shared/InputConfirm",
  argTypes: {},
};

export default meta;

type Story = StoryObj<typeof InputConfirm>;

export const Default: Story = {
  args: {
    value: "test",
  },
};
