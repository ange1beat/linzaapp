import { Meta, StoryObj } from "@storybook/react";

import ProjectChangeName from "./index";

const meta: Meta<typeof ProjectChangeName> = {
  component: ProjectChangeName,
  title: "Features/Project/ChangeName",
  argTypes: {},
};

export default meta;

type Story = StoryObj<typeof ProjectChangeName>;

export const Default: Story = {
  argTypes: {},
  args: {
    project: { id: "1", name: "test project" },
  },
};
