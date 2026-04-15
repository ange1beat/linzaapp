import { Meta, StoryObj } from "@storybook/react";

import EditProjectFormEntity from "./index";

const meta: Meta<typeof EditProjectFormEntity> = {
  component: EditProjectFormEntity,
  title: "Entities/EditProjectForm",
  argTypes: {},
};

export default meta;

type Story = StoryObj<typeof EditProjectFormEntity>;

export const WithAvatar: Story = {
  argTypes: {},
  args: {
    data: {
      name: "Project228",
      avatarUrl: "https://placekitten.com/g/150/150",
    },
    errors: { name: "", avatarUrl: "" },
    onChange: () => {},
    onCancel: () => {},
    onSuccess: () => {},
  },
};

export const WithoutAvatar: Story = {
  argTypes: {},
  args: {
    data: {
      name: "Project228",
      avatarUrl: "",
    },
    errors: { name: "", avatarUrl: "" },
    onChange: () => {},
    onCancel: () => {},
    onSuccess: () => {},
  },
};

export const WithError: Story = {
  argTypes: {},
  args: {
    data: {
      name: "Project228",
      avatarUrl: "",
    },
    errors: { name: "error name!", avatarUrl: "error avatar!" },
    onChange: () => {},
    onCancel: () => {},
    onSuccess: () => {},
  },
};
