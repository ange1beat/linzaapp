import type { StoryObj } from "@storybook/react";

import { getLoggedUser } from "@/shared/storybook/mocks";

import UserChangeNamePage from "./index";

export const Default: StoryObj<typeof UserChangeNamePage> = {};

export default {
  title: "Pages/UserChangeNamePage",
  component: UserChangeNamePage,
  parameters: {
    mockData: [getLoggedUser],
  },
};
