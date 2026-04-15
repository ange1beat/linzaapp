import { Meta, StoryObj } from "@storybook/react";

import Filter from "./index";

const meta: Meta<typeof Filter> = {
  component: Filter,
  title: "shared/Filter",
};

export default meta;

type Story = StoryObj<typeof Filter>;

export const Default: Story = {
  args: {
    onChange: () => {},
    value: { status: ["works"] },
    groups: [
      {
        label: "Status",
        name: "status",
        options: [
          { value: "works", label: "Works" },
          { value: "stopped", label: "Stopped" },
        ],
      },
      {
        label: "Type source",
        name: "type-source",
        options: [
          { value: "telegram", label: "Telegram" },
          { value: "web", label: "Web" },
          { value: "vk", label: "VK" },
          { value: "ok", label: "OK" },
        ],
      },
    ],
  },
};
