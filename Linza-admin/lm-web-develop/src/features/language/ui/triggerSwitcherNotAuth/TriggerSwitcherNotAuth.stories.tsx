import { Meta, StoryObj } from "@storybook/react";

import TriggerSwitcherNotAuth from "./index";

const meta: Meta<typeof TriggerSwitcherNotAuth> = {
  component: TriggerSwitcherNotAuth,
  title: "features/TriggerSwitcherNotAuth",
  args: {},
};

export default meta;

type Story = StoryObj<typeof TriggerSwitcherNotAuth>;

export const Default: Story = {
  args: {},
};
