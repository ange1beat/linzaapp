import { Meta, StoryObj } from "@storybook/react";

import FolderItem from "./index";

const meta: Meta<typeof FolderItem> = {
  component: FolderItem,
  title: "entities/Folders/Item",
  args: {},
};

export default meta;

type Story = StoryObj<typeof FolderItem>;

export const Default: Story = {
  args: {
    onDelete: () => {},
    folder: {
      id: "1",
      name: "Folder 01.01.2024",
    },
  },
};
