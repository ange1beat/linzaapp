import type { StoryObj } from "@storybook/react";

import { getLoggedUser } from "@/shared/storybook/mocks";

import UserChangeTelegramPage from "./index";

export const Default: StoryObj<typeof UserChangeTelegramPage> = {};

export default {
  title: "Pages/UserChangeTelegramPage",
  component: UserChangeTelegramPage,
  parameters: {
    mockData: [getLoggedUser],
  },
};
