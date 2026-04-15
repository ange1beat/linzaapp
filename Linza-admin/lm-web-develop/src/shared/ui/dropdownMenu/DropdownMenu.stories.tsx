import { Meta, StoryObj } from "@storybook/react";

import DropdownMenu from "./index";

const meta: Meta<typeof DropdownMenu> = {
  component: DropdownMenu,
  title: "shared/DropdownMenu",
};

export default meta;

type Story = StoryObj<typeof DropdownMenu>;

export const Default: Story = {
  args: {
    items: [
      {
        text: <div>123</div>,
        theme: "normal",
      },
      {
        text: <div>123</div>,
        theme: "danger",
      },
      {
        text: <div>123</div>,
        theme: "danger",
        disabled: true,
      },
    ],
  },
};

export const DoubleNesting: Story = {
  args: {
    items: [
      {
        text: <div>123</div>,
        theme: "normal",
        items: [
          {
            text: <div>Double</div>,
            theme: "normal",
            action: () => {},
          },
          {
            text: <div>123</div>,
            theme: "normal",
            action: () => {},
          },
        ],
      },
      {
        text: <div>123</div>,
        theme: "danger",
      },
      {
        text: <div>123</div>,
        theme: "danger",
        disabled: true,
      },
    ],
  },
};

export const TripleNesting: Story = {
  args: {
    items: [
      {
        text: <div>123</div>,
        theme: "normal",
        items: [
          {
            text: <div>Second</div>,
            action: () => {},
            items: [
              {
                text: <div>Third</div>,
                action: () => {},
              },
              {
                text: <div>Favorite</div>,
                action: () => {},
              },
            ],
          },
        ],
      },
      {
        text: <div>123</div>,
        theme: "danger",
      },
      {
        text: <div>123</div>,
        theme: "danger",
        disabled: true,
      },
    ],
  },
};
