import { Meta, StoryObj } from "@storybook/react";

import { getAllFolders } from "@/shared/storybook/mocks";

import FoldersList from "./index";

const meta: Meta<typeof FoldersList> = {
  component: FoldersList,
  title: "entities/Folders/List",
  args: {},
  parameters: {
    mockData: [getAllFolders],
  },
};

export default meta;

type Story = StoryObj<typeof FoldersList>;

export const Default: Story = {
  args: {
    deleteAction: () => {},
    addAction: <button>Add</button>,
    projectId: "1",
  },
};
