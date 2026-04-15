import { StoryObj } from "@storybook/react";

import { memberList } from "@/shared/storybook/mocks";

import MembersListEntity from "./index";

export default {
  component: MembersListEntity,
  title: "Entities/Members/MembersList",
  args: {},
  parameters: {
    mockData: [memberList],
  },
};

type Story = StoryObj<typeof MembersListEntity>;

export const Default: Story = {
  args: {
    selected: ["1"],
  },
};
