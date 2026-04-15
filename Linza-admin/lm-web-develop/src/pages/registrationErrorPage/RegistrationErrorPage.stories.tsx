import type { StoryObj } from "@storybook/react";

import RegistrationErrorPage from "./index";

export const Default: StoryObj<typeof RegistrationErrorPage> = {
  args: {},
};

export default {
  title: "Pages/RegistrationError",
  component: RegistrationErrorPage,
};
