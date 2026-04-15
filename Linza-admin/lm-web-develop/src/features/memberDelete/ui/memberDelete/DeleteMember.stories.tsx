import { Meta, StoryObj } from "@storybook/react";

import MemberDelete from "./index";

const meta: Meta<typeof MemberDelete> = {
  component: MemberDelete,
  title: "features/MemberDelete",
  args: {},
};

export default meta;

type Story = StoryObj<typeof MemberDelete>;

export const Default: Story = {
  args: {
    isOpen: true,
    member: {
      id: "1",
      firstName: "John",
      lastName: "Wick",
    },
    onSuccess: () => {},
    onCancel: () => {},
  },
};
