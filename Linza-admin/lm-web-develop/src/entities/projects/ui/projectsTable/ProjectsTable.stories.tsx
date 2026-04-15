import { Ellipsis } from "@gravity-ui/icons";
import { Icon } from "@gravity-ui/uikit";
import { Meta, StoryObj } from "@storybook/react";

import { FavoriteProject } from "@/features/projectToggleFavorite";
import { fullHeight } from "@/shared/storybook/decorators";
import { favProjects, listProjects } from "@/shared/storybook/mocks";

import ProjectsTable from "./index";

const meta: Meta<typeof ProjectsTable> = {
  component: ProjectsTable,
  title: "Entities/Projects/ProjectsTable",
  argTypes: {},
};

export default meta;

type Story = StoryObj<typeof ProjectsTable>;

export const Default: Story = {
  argTypes: {},
  args: {
    headerActions: <button>add project</button>,
    createdBy: (userId) => `userID: ${userId}`,
    rowActions: () => <Icon data={Ellipsis} />,
    favoriteProject: () => (
      <FavoriteProject isFavorite={false} projectId={""} />
    ),
  },
  decorators: [fullHeight],
  parameters: {
    layout: "fullscreen",
    mockData: [listProjects, favProjects],
  },
};
