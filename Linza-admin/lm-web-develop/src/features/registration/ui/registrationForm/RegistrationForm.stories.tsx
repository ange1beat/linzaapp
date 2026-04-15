import { Meta, StoryObj } from "@storybook/react";

import RegistrationForm from "./index";

const meta: Meta<typeof RegistrationForm> = {
  component: RegistrationForm,
  title: "features/registration/RegistrationForm",
  argTypes: {},
};

export default meta;

type Story = StoryObj<typeof RegistrationForm>;

export const Default: Story = {
  argTypes: {},
};
