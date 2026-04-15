import { StoryObj } from "@storybook/react";

import ModalWindow from "./index";

export const Default: StoryObj<typeof ModalWindow> = {
  args: {
    children: <div>Modal content!</div>,
    isOpen: true,
    title: "Create new project",
    onClose: () => {},
  },
};

export default {
  title: "Shared/ModalWindow",
  component: ModalWindow,
};
