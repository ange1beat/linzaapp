import { StoryObj } from "@storybook/react";

import { SourceType } from "@/entities/sources/models/types";

import SourcesTypeEntity from "./index";

export const Web: StoryObj<typeof SourcesTypeEntity> = {
  args: {
    type: SourceType.Web,
  },
};
export const OK: StoryObj<typeof SourcesTypeEntity> = {
  args: {
    type: SourceType.OK,
  },
};
export const VK: StoryObj<typeof SourcesTypeEntity> = {
  args: {
    type: SourceType.VK,
  },
};
export const Telegram: StoryObj<typeof SourcesTypeEntity> = {
  args: {
    type: SourceType.Telegram,
  },
};

export default {
  title: "Entities/Source/SourcesType",
  component: SourcesTypeEntity,
};
