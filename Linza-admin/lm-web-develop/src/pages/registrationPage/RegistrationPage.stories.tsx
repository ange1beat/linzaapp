import type { StoryObj } from "@storybook/react";

import { getUserInvitation } from "../../shared/storybook/mocks/usersAPI";

import RegistrationPage from "./index";

export const Default: StoryObj<typeof RegistrationPage> = {
  args: {},
};

export default {
  title: "Pages/RegistrationPage",
  component: RegistrationPage,

  parameters: {
    query: {
      invitationId: "123412341",
    },
    mockData: [getUserInvitation],
  },
};
