import { Smartphone } from "@gravity-ui/icons";
import { Meta, StoryObj } from "@storybook/react";

import Input from "./index";

const meta: Meta<typeof Input> = {
  component: Input,
  title: "shared/Input",
  argTypes: {
    size: {
      options: ["l", "s", "m", "xl"],
      control: { type: "radio" },
    },
  },
};

export default meta;

type Story = StoryObj<typeof Input>;

export const Default: Story = {
  args: {
    placeholder: "Write something",
  },
};

export const WithError: Story = {
  args: {
    isError: true,
    errorMessage: "Error!",
  },
};

export const WithRightContent: Story = {
  args: {
    rightContent: <Smartphone />,
  },
};
