import { Meta, StoryObj } from "@storybook/react";

import Timer from "./index";

const meta: Meta<typeof Timer> = {
  component: Timer,
  title: "shared/Timer",
};

export default meta;

type Story = StoryObj<typeof Timer>;

export const Default: Story = {
  args: {
    className: "class",
    timer: 10,
    actions: () => {
      return <div onClick={() => {}}>Reset code</div>;
    },
    template: (val) => `Request again in ${val}`,
    countDownEndText: "Requested again to",
  },
};
