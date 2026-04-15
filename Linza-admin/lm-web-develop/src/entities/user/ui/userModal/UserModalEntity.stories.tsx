import { StoryObj } from "@storybook/react";

import UserModalEntity from "./index";

export const Default: StoryObj<typeof UserModalEntity> = {
  args: {
    email: "user@mail.com",
    firstName: "Name",
    lastName: "Surname",
    avatar:
      "https://fastly.picsum.photos/id/237/200/300.jpg?hmac=TmmQSbShHz9CdQm0NkEjx1Dyh_Y984R9LpNrpvH2D_U",
  },
};

export const Overflow: StoryObj<typeof UserModalEntity> = {
  args: {
    email: "wjdajwdhawhdawjhduawhduawhduawhduawhud@nauk.ru",
    firstName: "ohmygodwhythisfirstnameissobig",
    lastName: "mylastnamesobigiwasprettyanswered",
    avatar:
      "https://fastly.picsum.photos/id/790/200/300.jpg?hmac=FVbUQYv_h5C4v5_RAIja_q1c5UShyHhRu6C7DvjZM8U",
  },
};

export const DefaultAvatar: StoryObj<typeof UserModalEntity> = {
  args: {
    email: "mailwithout@avatar.ru",
    firstName: "I havent",
    lastName: "avatar",
  },
};

export default {
  title: "Entities/UserModal",
  component: UserModalEntity,
};
