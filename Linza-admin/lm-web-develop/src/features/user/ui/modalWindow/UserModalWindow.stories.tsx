import { Meta, StoryObj } from "@storybook/react";

import { revokeToken } from "../../../../shared/storybook/mocks/authAPI";
import { getLoggedUser } from "../../../../shared/storybook/mocks/usersAPI";

import UserModalWindow from "./index";

const meta: Meta<typeof UserModalWindow> = {
  component: UserModalWindow,
  title: "Features/UserModalWindow",
  parameters: {
    mockData: [getLoggedUser, revokeToken],
  },
};

export default meta;

type Story = StoryObj<typeof UserModalWindow>;

export const Default: Story = {
  args: {},
};
