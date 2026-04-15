import { Meta, StoryObj } from "@storybook/react";

import Button from "@/shared/ui/button";

import SwitcherLanguage from "./index";

const meta: Meta<typeof SwitcherLanguage> = {
  component: SwitcherLanguage,
  title: "features/SwitcherLanguage",
  args: {},
};

export default meta;

type Story = StoryObj<typeof SwitcherLanguage>;

export const Default: Story = {
  args: {
    children: <Button view="normal">Switch element</Button>,
  },
};
