import { Meta, StoryObj } from "@storybook/react";

import { selectedMember } from "@/shared/storybook/mocks/membersAPI";

import { EditMemberPasswordFormEntity } from "./index";

const meta: Meta<typeof EditMemberPasswordFormEntity> = {
  component: EditMemberPasswordFormEntity,
  title: "Entities/EditMemberPasswordForm",
  argTypes: {},
};

export default meta;

type Story = StoryObj<typeof EditMemberPasswordFormEntity>;

export const Default: Story = {
  argTypes: {},
  args: {
    memberId: "1",
    isOpen: true,
    isLoad: false,
    onSubmit: () => {},
    onChange: () => {},
    onCancel: () => {},
    errors: { newPassword: "", confirmPassword: "" },
  },
  parameters: {
    mockData: [selectedMember],
  },
};
