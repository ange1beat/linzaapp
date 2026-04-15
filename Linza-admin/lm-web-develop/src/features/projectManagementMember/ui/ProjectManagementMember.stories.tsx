import { Meta, StoryObj } from "@storybook/react";

import {
  deleteMemberFromProject,
  addMemberToProject,
  memberList,
} from "@/shared/storybook/mocks";

import MemberManagementProject from "./index";

const meta: Meta<typeof MemberManagementProject> = {
  component: MemberManagementProject,
  title: "Features/Project/MemberManagementProject",
  args: { projectId: "1" },
  parameters: {
    mockData: [deleteMemberFromProject, addMemberToProject, memberList],
  },
};

export default meta;

type Story = StoryObj<typeof MemberManagementProject>;

export const Default: Story = {};
