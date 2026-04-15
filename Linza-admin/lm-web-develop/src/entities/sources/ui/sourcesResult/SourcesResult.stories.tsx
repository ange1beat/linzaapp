import { Meta, StoryObj } from "@storybook/react";

import { SourceLastResult } from "@/entities/sources/models/types";

import SourcesResultEntity from "./index";

const meta: Meta<typeof SourcesResultEntity> = {
  component: SourcesResultEntity,
  title: "entities/Source/SourcesResult",
  args: {},
};

export default meta;

type Story = StoryObj<typeof SourcesResultEntity>;

export const Error: Story = {
  args: {
    status: SourceLastResult.Error,
  },
};
export const Success: Story = {
  args: {
    status: SourceLastResult.Success,
  },
};
export const Without: Story = {
  args: {
    status: undefined,
  },
};
