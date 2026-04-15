import { StoryObj } from "@storybook/react";

import ProfilePage from "./index";

export const Default: StoryObj<typeof ProfilePage> = {
  args: {
    user: {
      id: "1",
      firstName: "Rukka",
      lastName: "Rukkalo",
      telegramUsername: "@rukkalo",
      phoneNumber: "+78005553535",
      email: "rukka69@examplesuperoverflowemail.com",
      roles: ["User"],
      avatarUrl: "https://placekitten.com/g/200/300",
    },
  },
};
export const Minimal: StoryObj<typeof ProfilePage> = {
  args: {
    user: {
      id: "1",
      firstName: "Rukka",
      lastName: "Rukkalo",
      email: "rukka69@examplesuperoverflowemail.com",
      roles: ["User"],
    },
  },
};

export const Load: StoryObj<typeof ProfilePage> = {
  args: {
    isLoad: true,
    user: {
      id: "1",
      firstName: "Rukka",
      lastName: "Rukkalo",
      telegramUsername: "@rukkalo",
      phoneNumber: "+78005553535",
      email: "rukka69@examplesuperoverflowemail.com",
      roles: ["User"],
      avatarUrl: "https://placekitten.com/g/200/300",
    },
  },
};

export default {
  title: "Pages/ProfilePage",
  component: ProfilePage,
};
