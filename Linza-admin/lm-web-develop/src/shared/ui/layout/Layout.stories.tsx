import { Gear } from "@gravity-ui/icons";
import { Meta, StoryObj } from "@storybook/react";

import Button from "../button";

import Layout from "./index";

const meta: Meta<typeof Layout> = {
  component: Layout,
  title: "shared/Layout",
};

export default meta;

const breadCrumbsItems = [
  {
    text: "Page",
    link: "/page",
  },
];

type Story = StoryObj<typeof Layout>;

export const Default: Story = {
  args: {
    items: breadCrumbsItems,
  },
};

export const WithActions: Story = {
  args: {
    items: breadCrumbsItems,
    actions: (
      <Button size="m" iconLeft={<Gear />} view="normal">
        Settings
      </Button>
    ),
  },
};

export const WithContent: Story = {
  args: {
    items: breadCrumbsItems,
    children: (
      <Button size="m" iconLeft={<Gear />} view="normal">
        Settings
      </Button>
    ),
  },
};
