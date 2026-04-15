import type { StoryObj } from "@storybook/react";

import RegistrationSuccessPage from "./index";

export const Default: StoryObj<typeof RegistrationSuccessPage> = {
  args: {},
};

export default {
  title: "Pages/RegistrationSuccess",
  component: RegistrationSuccessPage,
};
