import type { StoryObj } from "@storybook/react";

import ProjectFolders from "./index";

export const Default: StoryObj<typeof ProjectFolders> = {
  args: {},
};

export default {
  title: "Pages/ProjectFolders",
  component: ProjectFolders,
};
