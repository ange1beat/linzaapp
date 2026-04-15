import { StoryObj } from "@storybook/react";

import Pagination from "./index";

export const Default: StoryObj<typeof Pagination> = {
  args: {
    page: 1,
    pageSize: 10,
    total: 30,
    pageSizeOptions: [5, 10, 20, 50, 100],
  },
};

export default {
  title: "Shared/Pagination",
  component: Pagination,
};
