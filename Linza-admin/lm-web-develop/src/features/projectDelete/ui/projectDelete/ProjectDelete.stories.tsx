import { Meta, StoryObj } from "@storybook/react";

import DeleteProject from "./index";

const meta: Meta<typeof DeleteProject> = {
  component: DeleteProject,
  title: "Features/Project/DeleteProject",
  args: {},
};

export default meta;

type Story = StoryObj<typeof DeleteProject>;

export const Default: Story = {
  args: {
    project: { id: "1", name: "Test project" },
    isOpen: true,
    onClose: () => {},
  },
};
