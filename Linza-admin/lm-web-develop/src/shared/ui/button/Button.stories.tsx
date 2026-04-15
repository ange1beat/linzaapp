import { Gear } from "@gravity-ui/icons";
import { Icon } from "@gravity-ui/uikit";
import { StoryObj } from "@storybook/react";

import Button from "./index";

export const Default: StoryObj<typeof Button> = {
  args: {
    width: "auto",
    children: <span>Button!</span>,
    view: "normal",
  },
};

export const Disabled: StoryObj<typeof Button> = {
  args: {
    disabled: true,
    children: <span>Button!</span>,
  },
};

export const Loaded: StoryObj<typeof Button> = {
  args: {
    loading: true,
    children: <span>Button!</span>,
  },
};

export const WithStyle: StoryObj<typeof Button> = {
  args: {
    className: "class",
    children: <span>Styled button</span>,
  },
};

export const WithIconLeft: StoryObj<typeof Button> = {
  args: {
    iconLeft: <Icon data={Gear} />,
    children: <span>Styled button</span>,
  },
};

export const WithIconRight: StoryObj<typeof Button> = {
  args: {
    iconRight: <Icon data={Gear} />,
    children: <span>Styled button</span>,
  },
};

export default {
  title: "Shared/Button",
  component: Button,
};
