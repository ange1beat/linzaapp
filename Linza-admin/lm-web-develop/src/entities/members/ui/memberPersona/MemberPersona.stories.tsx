import { Meta, StoryObj } from "@storybook/react";

import MemberPersona from "./index";

const meta: Meta<typeof MemberPersona> = {
  component: MemberPersona,
  title: "Entities/Members/MemberPersona",
  args: { memberId: "1" },
};

export default meta;

type Story = StoryObj<typeof MemberPersona>;

export const Default: Story = {};
