import { Meta, StoryObj } from "@storybook/react";

import ProjectChangeAvatar from "./index";

const meta: Meta<typeof ProjectChangeAvatar> = {
  component: ProjectChangeAvatar,
  title: "Features/Project/ProjectChangeAvatar",
  args: {},
};

export default meta;

type Story = StoryObj<typeof ProjectChangeAvatar>;

export const WithAvatar: Story = {
  args: {
    project: {
      id: "2",
      avatarUrl:
        "https://robohash.org/optioofficiabeatae.png?size=50x50&set=set1",
    },
  },
};

export const WithoutAvatar: Story = {
  args: {
    project: {
      id: "2",
      avatarUrl: null,
    },
  },
};
