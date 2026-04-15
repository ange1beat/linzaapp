import type { StoryObj } from "@storybook/react";

import { MemberDetailPage } from "@/pages/index";

export const Default: StoryObj<typeof MemberDetailPage> = {
  args: {},
};

export default {
  title: "Pages/MemberDetailPage",
  component: MemberDetailPage,
};
