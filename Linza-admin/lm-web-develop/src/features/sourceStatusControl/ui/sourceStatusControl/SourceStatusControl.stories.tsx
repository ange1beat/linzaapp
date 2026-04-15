import { Meta, StoryObj } from "@storybook/react";

import {
  SourceExecutionStatus,
  SourceLastResult,
  SourceType,
} from "@/entities/sources/models/types";
import {
  updateSourceByIdOff,
  updateSourceByIdOn,
} from "@/shared/storybook/mocks/sourceAPI";

import SourceStatusControlFeature from "./index";

const meta: Meta<typeof SourceStatusControlFeature> = {
  component: SourceStatusControlFeature,
  title: "Features/Source/SourceStatusControlFeature",
  args: {},
};

export default meta;

type Story = StoryObj<typeof SourceStatusControlFeature>;

export const Active: Story = {
  args: {
    source: {
      id: "6d5aeba3-dcd9-425c-9b74-cf0c2dae2347",
      created: "2022-08-06T17:37:26.235028+00:00",
      modified: "2022-08-06T17:37:26.235028+00:00",
      title: "alania_gov",
      description: "",
      iconUri: "",
      type: SourceType.Telegram,
      url: "https://t.me/alania_gov",
      updateInterval: 3600,
      isActive: true,
      isAutoCreated: true,
      config: {},
      account: {},
      timezone: "Europe/Moscow",
      updated: "2022-08-06T17:37:26.235026+00:00",
      lastResult: SourceLastResult.Success,
      nextLaunch: 4824,
      executionStatus: SourceExecutionStatus.Stopped,
    },
  },
  parameters: {
    mockData: [updateSourceByIdOn],
  },
};

export const Inactive: Story = {
  args: {
    source: {
      id: "6d5aeba3-dcd9-425c-9b74-cf0c2dae2347",
      created: "2022-08-06T17:37:26.235028+00:00",
      modified: "2022-08-06T17:37:26.235028+00:00",
      title: "alania_gov",
      description: "",
      iconUri: "",
      type: SourceType.Telegram,
      url: "https://t.me/alania_gov",
      updateInterval: 3600,
      isActive: false,
      isAutoCreated: true,
      config: {},
      account: {},
      timezone: "Europe/Moscow",
      updated: "2022-08-06T17:37:26.235026+00:00",
      lastResult: SourceLastResult.Success,
      nextLaunch: 4824,
      executionStatus: SourceExecutionStatus.Stopped,
    },
  },
  parameters: {
    mockData: [updateSourceByIdOff],
  },
};
