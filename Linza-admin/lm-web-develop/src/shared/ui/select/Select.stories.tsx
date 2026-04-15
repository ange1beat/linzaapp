import { StoryObj } from "@storybook/react";

import Select from "./index";

export const Default: StoryObj<typeof Select> = {
  args: {
    placeholder: "Placeholder",
    options: [
      { value: "User", label: "User" },
      { value: "2", label: "second" },
      { value: "3", label: "third" },
    ],
  },
};

export const WithValue: StoryObj<typeof Select> = {
  args: {
    placeholder: "Placeholder",
    value: "User",
    options: [
      { value: "User", label: "User" },
      { value: "2", label: "second" },
      { value: "3", label: "third" },
    ],
  },
};

export default {
  title: "Shared/Select",
  component: Select,
};
