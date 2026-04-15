import React from "react";

import type { StoryObj } from "@storybook/react";

import ProjectsPage from "./index";

export const Default: StoryObj<typeof ProjectsPage> = {
  args: {
    children: <div>here must be some children</div>,
  },
};

export default {
  title: "Pages/ProjectsPage",
  component: ProjectsPage,
};
