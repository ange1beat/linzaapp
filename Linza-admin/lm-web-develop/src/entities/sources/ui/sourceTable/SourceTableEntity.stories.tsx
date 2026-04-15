import { Meta, StoryObj } from "@storybook/react";

import { getSources } from "@/shared/storybook/mocks/sourceAPI";

import SourceTableEntity from "./index";

const meta: Meta<typeof SourceTableEntity> = {
  component: SourceTableEntity,
  title: "Entities/Source/SourceTable",
  argTypes: {},
};

export default meta;

type Story = StoryObj<typeof SourceTableEntity>;

export const Default: Story = {
  argTypes: {},
  args: {
    statusControl: () => <div>...</div>,
    actions: () => <div>...</div>,
    headerActions: <div>...</div>,
  },
  parameters: {
    mockData: [getSources],
  },
};
