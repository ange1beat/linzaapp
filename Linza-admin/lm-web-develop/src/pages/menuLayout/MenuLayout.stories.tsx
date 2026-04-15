import React from "react";

import type { StoryObj } from "@storybook/react";

import MenuLayout from "./index";

export const Default: StoryObj<typeof MenuLayout> = {
  args: {
    children: <div>here must be some children</div>,
  },
};

export default {
  title: "Pages/MenuLayout",
  component: MenuLayout,
};
