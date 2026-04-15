import { Meta, StoryObj } from "@storybook/react";

import EditMember from "./index";

const meta: Meta<typeof EditMember> = {
  component: EditMember,
  title: "entities/EditMember",
  args: {
    data: {
      id: "1",
      firstName: "First Name",
      lastName: "Last Name",
      email: "Email",
      phoneNumber: "88005553535",
      telegramUsername: "Telegram",
    },
  },
};

export default meta;

type Story = StoryObj<typeof EditMember>;

export const Default: Story = {
  args: {},
};
