import { Meta, StoryObj } from "@storybook/react";

import { getLoggedUser, updateUserName } from "@/shared/storybook/mocks";

import UserChangeNameFeature from "./index";

const meta: Meta<typeof UserChangeNameFeature> = {
  component: UserChangeNameFeature,
  title: "Features/User/ChangeName",
  argTypes: {},
  parameters: {
    mockData: [updateUserName, getLoggedUser],
  },
};

export default meta;

type Story = StoryObj<typeof UserChangeNameFeature>;

export const Default: Story = {
  argTypes: {},
  args: {},
};
