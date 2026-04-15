import { Meta, StoryObj } from "@storybook/react";

import { deleteFolder } from "@/shared/storybook/mocks";

import FolderDelete from "./index";

const meta: Meta<typeof FolderDelete> = {
  component: FolderDelete,
  title: "Features/Folder/FolderDelete",
  argTypes: {},
};

export default meta;

type Story = StoryObj<typeof FolderDelete>;

export const Default: Story = {
  argTypes: {},
  args: {
    isOpen: true,
    folder: { id: "1", name: "Folder 01.01.2024" },
    projectId: "1",
    onCancel: () => {},
  },
  parameters: {
    mockData: [deleteFolder],
  },
};
