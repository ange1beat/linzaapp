import { Meta, StoryObj } from "@storybook/react";

import {
  getProjectsOfMember,
  modifyMembershipProjects,
} from "@/shared/storybook/mocks";

import MemberManagementProject from "./index";

const meta: Meta<typeof MemberManagementProject> = {
  component: MemberManagementProject,
  title: "Features/Member/MemberManagementProject",
  args: { memberId: "1" },
  parameters: {
    mockData: [getProjectsOfMember, modifyMembershipProjects],
  },
};

export default meta;

type Story = StoryObj<typeof MemberManagementProject>;

export const Default: Story = {};
