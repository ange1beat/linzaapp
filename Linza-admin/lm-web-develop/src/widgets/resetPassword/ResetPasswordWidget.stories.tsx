import { StoryObj } from "@storybook/react";

import ResetPasswordWidget from "./index";

export const Default: StoryObj<typeof ResetPasswordWidget> = {
  args: {},
};

export default {
  title: "Widgets/ResetPassword",
  component: ResetPasswordWidget,
};
