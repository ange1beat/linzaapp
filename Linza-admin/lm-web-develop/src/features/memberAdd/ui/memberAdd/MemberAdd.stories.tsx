import { Meta, StoryObj } from "@storybook/react";

import MemberAdd from "./index";

const meta: Meta<typeof MemberAdd> = {
  component: MemberAdd,
  title: "Features/Member/MemberAdd",
  args: { children: <button>Open Modal</button> },
};

export default meta;

type Story = StoryObj<typeof MemberAdd>;

export const Default: Story = {};
