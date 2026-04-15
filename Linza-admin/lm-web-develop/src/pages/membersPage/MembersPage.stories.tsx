import type { StoryObj } from "@storybook/react";

import MembersPage from "./index";

export const Default: StoryObj<typeof MembersPage> = {
  args: {},
};

export default {
  title: "Pages/MembersPage",
  component: MembersPage,
};
