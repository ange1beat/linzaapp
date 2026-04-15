import { Meta, StoryObj } from "@storybook/react";

import Avatar from "./index";

const meta: Meta<typeof Avatar> = {
  component: Avatar,
  title: "shared/Avatar",
};

export default meta;

type Story = StoryObj<typeof Avatar>;

export const Default: Story = {
  args: {
    isLoad: false,
    avatar: "",
    onChange: (ava) => ava,
  },
};

export const AvatarExist: Story = {
  args: {
    isLoad: false,
    avatar: "https://shorturl.at/goAC2",
    onChange: (ava) => ava,
  },
};

export const AvatarExistWithError: Story = {
  args: {
    isLoad: false,
    avatar: "https://shorturl.at/goAC2",
    onChange: (ava) => ava,
    error: "ERROR error 434238743878234973228489",
  },
};

export const AvatarLoad: Story = {
  args: {
    isLoad: true,
    avatar: "https://shorturl.at/goAC2",
    onChange: (ava) => ava,
  },
};
