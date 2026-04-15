import { Meta, StoryObj } from "@storybook/react";

import ProjectAdd from "./index";

const meta: Meta<typeof ProjectAdd> = {
  component: ProjectAdd,
  title: "Features/Project/Add",
  args: {},
};

export default meta;

type Story = StoryObj<typeof ProjectAdd>;

export const Default: Story = {
  args: {
    isOpen: true,
  },
};
