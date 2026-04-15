import { StoryObj } from "@storybook/react";

import UserMenuItem from "./index";

export const Default: StoryObj<typeof UserMenuItem> = {
  args: {
    avatar: "https://placekitten.com/g/100/100",
  },
};

export const WithoutAvatar: StoryObj<typeof UserMenuItem> = {
  args: {},
};

export default {
  title: "Entities/UserMenuItem",
  component: UserMenuItem,
};
