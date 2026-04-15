import { Meta, StoryObj } from "@storybook/react";

import { listProjects } from "@/shared/storybook/mocks";

import ProjectsListEntity from "./index";

const meta: Meta<typeof ProjectsListEntity> = {
  component: ProjectsListEntity,
  title: "Entities/ProjectsList",
  argTypes: {},
};

export default meta;

type Story = StoryObj<typeof ProjectsListEntity>;

export const Default: Story = {
  argTypes: {},
  args: {
    onDeselect: () => {},
    onSelect: () => {},
    isDisabled: false,
    selected: [],
  },
  parameters: {
    mockData: [listProjects],
  },
};
