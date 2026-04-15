import { Meta, StoryObj } from "@storybook/react";

import BreadCrumbs from "./index";

const meta: Meta<typeof BreadCrumbs> = {
  component: BreadCrumbs,
  title: "shared/BreadCrumbs",
  argTypes: {},
};

export default meta;

type Story = StoryObj<typeof BreadCrumbs>;

export const Default: Story = {
  args: {
    items: [
      {
        text: "Squad Ready IT",
        link: "/squad-ready",
      },
    ],
  },
};

export const Multiple: Story = {
  args: {
    items: [
      {
        text: "Squad Ready IT",
        link: "/squad-ready",
      },
      {
        text: "Another",
        link: "/",
      },
      {
        text: "Some",
        link: "/",
      },
    ],
  },
};
