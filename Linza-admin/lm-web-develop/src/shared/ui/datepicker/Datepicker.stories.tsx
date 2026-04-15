import { StoryObj } from "@storybook/react";

import Datepicker from "./index";

export const Default: StoryObj<typeof Datepicker> = {
  args: {
    value: { startDate: new Date(2024, 1, 1), endDate: new Date(2024, 1, 10) },
  },
};

export default {
  title: "Shared/DatePicker",
  component: Datepicker,
};
