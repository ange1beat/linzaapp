import { Meta, StoryObj } from "@storybook/react";

import { fullHeight } from "@/shared/storybook/decorators";
import {
  addProjectToFav,
  deleteProjectFromFav,
} from "@/shared/storybook/mocks";

import FavoriteProject from "./index";

const meta: Meta<typeof FavoriteProject> = {
  component: FavoriteProject,
  title: "Features/Project/FavoriteProject",
  argTypes: {},
};

export default meta;

type Story = StoryObj<typeof FavoriteProject>;

export const Default: Story = {
  argTypes: {},
  args: {
    isFavorite: false,
    projectId: "1",
  },
  decorators: [fullHeight],
  parameters: {
    layout: "fullscreen",
    mockData: [addProjectToFav, deleteProjectFromFav],
  },
};
