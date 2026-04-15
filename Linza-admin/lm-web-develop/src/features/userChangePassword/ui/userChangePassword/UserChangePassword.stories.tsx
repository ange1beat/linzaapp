import { Meta, StoryObj } from "@storybook/react";

import { changeLoggedUserPassword } from "@/shared/storybook/mocks";

import UserChangePassword from "./index";

const meta: Meta<typeof UserChangePassword> = {
  component: UserChangePassword,
  title: "Features/User/ChangePassword",
  argTypes: {},
};

export default meta;

type Story = StoryObj<typeof UserChangePassword>;

export const Default: Story = {
  argTypes: {},
  args: {},
  parameters: {
    mockData: [changeLoggedUserPassword],
  },
};
