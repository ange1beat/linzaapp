import React from "react";

import type { StoryObj } from "@storybook/react";

import BaseLayout from "./index";

export const Default: StoryObj<typeof BaseLayout> = {
  args: {
    children: <div>here must be some children</div>,
  },
};

export default {
  title: "Pages/BaseLayout",
  component: BaseLayout,
};
