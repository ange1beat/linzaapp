import { StoryObj } from "@storybook/react";

import Alert from "./alert";

export const Success: StoryObj<typeof Alert> = {
  args: {
    id: 1,
    options: {
      title: "Alert title",
      message: "alert message",
      theme: "success",
    },
  },
};

export const Warning: StoryObj<typeof Alert> = {
  args: {
    id: 1,
    options: {
      title: "Alert title",
      message: "alert message",
      theme: "warning",
    },
  },
};

export const Danger: StoryObj<typeof Alert> = {
  args: {
    id: 1,
    options: {
      title: "Alert title",
      message: "alert message",
      theme: "danger",
    },
  },
};

export default {
  title: "Shared/Alert",
  component: Alert,
};
