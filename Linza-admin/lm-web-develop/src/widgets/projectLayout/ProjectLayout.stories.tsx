import { StoryObj } from "@storybook/react";

import ProjectLayout from "./index";

export const Default: StoryObj<typeof ProjectLayout> = {
  args: {
    currentTab: "folders",
    projectId: "1",
  },
};

export default {
  title: "Widgets/ProjectLayout",
  component: ProjectLayout,
};
