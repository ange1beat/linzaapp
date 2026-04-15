import type { StoryObj } from "@storybook/react";

import Persona from "./index";

export default {
  component: Persona,
  title: "shared/Persona",
  argTypes: {
    size: {
      options: ["xxs", "n", "s"],
      control: { type: "radio" },
    },
    disabled: {
      control: "boolean",
    },
  },
};

type Story = StoryObj<typeof Persona>;

export const Default: Story = {
  args: {
    text: "Default text",
    image: "https://robohash.org/quoofficiasint.png?size=50x50&set=set1",
    size: "n",
  },
};
