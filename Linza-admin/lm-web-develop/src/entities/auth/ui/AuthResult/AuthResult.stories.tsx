import { Meta, StoryObj } from "@storybook/react";

import AuthResult from "./index";

const meta: Meta<typeof AuthResult> = {
  component: AuthResult,
  title: "entities/Auth/AuthResult",
  argTypes: {},
};

export default meta;

export const Success: StoryObj<typeof AuthResult> = {
  args: {
    title: "Successfully",
    message:
      "You have successfully completed registration. You can now log in to start using Linza.",
    header: <h3 style={{ margin: 0 }}>Registration in Linza</h3>,
    linkText: "Go to login page",
    link: "/login",
    isSuccess: true,
  },
};

export const Error: StoryObj<typeof AuthResult> = {
  args: {
    title: "Invitation expired",
    message:
      "Please, request a new invitation by your provider. The invitation is valid for 7 days.",
    header: <h3 style={{ margin: 0 }}>Registration in Linza</h3>,
    linkText: "Go to login page",
    link: "/login",
    isSuccess: false,
  },
};
