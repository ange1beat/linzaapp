import { Plus } from "@gravity-ui/icons";
import { Meta, StoryObj } from "@storybook/react";

import { Button } from "@/shared/ui";

import ProjectMembersTable from "./index";

const meta: Meta<typeof ProjectMembersTable> = {
  component: ProjectMembersTable,
  title: "Entities/Projects/ProjectMembersTable",
  argTypes: {},
};

export default meta;

type Story = StoryObj<typeof ProjectMembersTable>;

export const Default: Story = {
  argTypes: {},
  args: {
    projectId: "1",
    rowActions: () => (
      <Button view="normal" size="xs" onClick={() => alert("some action")}>
        ...
      </Button>
    ),
    headActions: (
      <Button view="normal">
        <Plus /> Add Member
      </Button>
    ),
  },
};
