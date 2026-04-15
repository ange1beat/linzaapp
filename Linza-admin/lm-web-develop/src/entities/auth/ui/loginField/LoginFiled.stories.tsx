import { Meta, StoryObj } from "@storybook/react";

import LoginFiledFeature from "./index";

const meta: Meta<typeof LoginFiledFeature> = {
  component: LoginFiledFeature,
  title: "features/LoginFiledFeature",
  args: {},
};

export default meta;

type Story = StoryObj<typeof LoginFiledFeature>;

export const Default: Story = {
  args: {},
};
