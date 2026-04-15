import { Meta, StoryObj } from "@storybook/react";

import EmailForm from "./index";

const meta: Meta<typeof EmailForm> = {
  component: EmailForm,
  title: "Features/userChangeEmail/EmailForm",
  argTypes: {},
};

export default meta;

type Story = StoryObj<typeof EmailForm>;

export const Default: Story = {
  argTypes: {},
  args: {},
};
