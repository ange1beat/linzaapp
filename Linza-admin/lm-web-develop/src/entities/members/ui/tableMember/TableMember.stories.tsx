import { Meta, StoryObj } from "@storybook/react";

import { fullHeight } from "@/shared/storybook/decorators";
import { memberList } from "@/shared/storybook/mocks";
import { Button } from "@/shared/ui";

import TableMember from "./index";

const meta: Meta<typeof TableMember> = {
  component: TableMember,
  title: "Entities/Members/TableMember",
  argTypes: {},
};

export default meta;

type Story = StoryObj<typeof TableMember>;

export const Default: Story = {
  argTypes: {},
  args: {
    rowActions: () => "...",
    headerActions: <Button view="normal">Add user</Button>,
  },
  decorators: [fullHeight],
  parameters: {
    layout: "fullscreen",
    mockData: [memberList],
  },
};
