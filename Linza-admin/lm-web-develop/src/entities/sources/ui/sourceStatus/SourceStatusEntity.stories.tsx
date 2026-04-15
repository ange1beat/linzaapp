import { Meta, StoryObj } from "@storybook/react";

import { SourceExecutionStatus } from "@/entities/sources/models/types";

import SourceStatusEntity from "./index";

const meta: Meta<typeof SourceStatusEntity> = {
  component: SourceStatusEntity,
  title: "Entities/Source/SourceStatus",
  argTypes: {},
};

export default meta;

type Story = StoryObj<typeof SourceStatusEntity>;

export const Planned: Story = {
  argTypes: {},
  args: {
    executionStatus: SourceExecutionStatus.Planned,
  },
};
export const InProgress: Story = {
  argTypes: {},
  args: {
    executionStatus: SourceExecutionStatus.InProgress,
  },
};
export const Stopped: Story = {
  argTypes: {},
  args: {
    executionStatus: SourceExecutionStatus.Stopped,
  },
};
export const NotConfigure: Story = {
  argTypes: {},
  args: {
    executionStatus: SourceExecutionStatus.NotConfigure,
  },
};
