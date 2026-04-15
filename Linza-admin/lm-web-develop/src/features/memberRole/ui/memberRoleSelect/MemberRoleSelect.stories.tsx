import { Meta, StoryObj } from "@storybook/react";

import { USER_ROLES } from "@/shared/config";

import MemberRoleSelect from "./index";

const meta: Meta<typeof MemberRoleSelect> = {
  component: MemberRoleSelect,
  title: "Features/Member/RoleSelect",
  args: {
    member: {
      id: "1",
      roles: [USER_ROLES.Supervisor],
    },
  },
};

export default meta;

type Story = StoryObj<typeof MemberRoleSelect>;

export const Default: Story = {};
