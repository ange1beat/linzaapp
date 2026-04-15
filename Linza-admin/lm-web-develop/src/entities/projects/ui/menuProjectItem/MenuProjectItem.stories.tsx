import { Meta, StoryObj } from "@storybook/react";

import MenuProjectItem from "./index";

const meta: Meta<typeof MenuProjectItem> = {
  component: MenuProjectItem,
  title: "Entities/Projects/MenuProjectItem",
};

export default meta;

type Story = StoryObj<typeof MenuProjectItem>;

export const Default: Story = {
  argTypes: {},
};
