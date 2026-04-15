import { StoryObj } from "@storybook/react";

import Link from "./index";

export const Default: StoryObj<typeof Link> = {
  args: {
    children: "TestLink",
  },
};

export default {
  title: "Shared/Link",
  component: Link,
};
