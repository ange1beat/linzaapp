import type { StoryObj } from "@storybook/react";

import Button from "../button";

import windowFrame from "./index";

export const Default: StoryObj<typeof windowFrame> = {
  args: {
    title: "TestTitle",
    children: (
      <>
        <Button view={"action"}>{"test"}</Button>
      </>
    ),
  },
};

export default {
  title: "Shared/windowFrame",
  component: windowFrame,
};
