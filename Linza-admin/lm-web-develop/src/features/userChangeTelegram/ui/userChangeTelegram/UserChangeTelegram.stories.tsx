import { Meta, StoryObj } from "@storybook/react";

import UserChangeTelegram from "./index";

const meta: Meta<typeof UserChangeTelegram> = {
  component: UserChangeTelegram,
  title: "Features/User/ChangeTelegram",
  argTypes: {},
};

export default meta;

type Story = StoryObj<typeof UserChangeTelegram>;

export const Default: Story = {
  argTypes: {},
  args: {},
};
