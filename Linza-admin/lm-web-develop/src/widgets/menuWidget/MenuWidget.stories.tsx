import { StoryObj } from "@storybook/react";

import { revokeToken } from "@/shared/storybook/mocks/authAPI";
import {
  addProject,
  favProjects,
  listProjects,
  updateProjectAvatar,
} from "@/shared/storybook/mocks/projectsAPI";
import { getLoggedUser } from "@/shared/storybook/mocks/usersAPI";

import MenuWidget from "./index";

export const Default: StoryObj<typeof MenuWidget> = {
  args: {},
};

export default {
  title: "Widgets/MenuWidget",
  component: MenuWidget,
  parameters: {
    mockData: [
      getLoggedUser,
      revokeToken,
      listProjects,
      favProjects,
      addProject,
      updateProjectAvatar,
    ],
  },
};
