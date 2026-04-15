import type { StoryObj } from "@storybook/react";

import ProjectDetailsPage from "./index";

export const Default: StoryObj<typeof ProjectDetailsPage> = {
  args: {},
};

export default {
  title: "Pages/ProjectDetailsPage",
  component: ProjectDetailsPage,
};
