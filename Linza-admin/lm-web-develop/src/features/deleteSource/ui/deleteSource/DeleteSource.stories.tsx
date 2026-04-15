import { Meta, StoryObj } from "@storybook/react";

import {
  SourceExecutionStatus,
  SourceLastResult,
  SourceType,
} from "@/entities/sources/models/types";
import { deleteSourceById } from "@/shared/storybook/mocks/sourceAPI";

import DeleteSourceFeature from "./index";

const meta: Meta<typeof DeleteSourceFeature> = {
  component: DeleteSourceFeature,
  title: "Features/Source/DeleteSource",
  argTypes: {},
};

export default meta;

type Story = StoryObj<typeof DeleteSourceFeature>;

export const Default: Story = {
  argTypes: {},
  args: {
    isOpen: true,
    source: {
      id: "d921cc8c-9e26-43bf-b548-6698b772678f",
      created: "2023-06-09T22:13:04.269980+00:00",
      modified: "2024-01-18T07:25:44.044035+00:00",
      title: "16 \u043d\u0435\u0433\u0440\u0438\u0442\u044f\u0442",
      description: "",
      iconUri: "",
      type: SourceType.Telegram,
      url: "https://t.me/Gubery",
      updateInterval: 300,
      isActive: true,
      isAutoCreated: true,
      config: {},
      account: {},
      timezone: "Europe/Moscow",
      updated: "2023-06-09T22:13:04.269979+00:00",
      lastResult: SourceLastResult.Success,
      nextLaunch: 240,
      executionStatus: SourceExecutionStatus.InProgress,
    },
    onClose: () => {},
  },
  parameters: {
    mockData: [deleteSourceById],
  },
};
