import React from "react";

import { StoryObj } from "@storybook/react";

import { fullHeight } from "@/shared/storybook/decorators";

import TableLayout from "./index";

export const Default: StoryObj<typeof TableLayout> = {
  parameters: {
    layout: "fullscreen",
  },
  decorators: [fullHeight],
  args: {
    children: [
      <TableLayout.Header>search and filters</TableLayout.Header>,
      <TableLayout.Body>{"table ".repeat(1000)}</TableLayout.Body>,
      <TableLayout.Footer>Pagination</TableLayout.Footer>,
    ],
  },
};

export default {
  title: "Shared/TableLayout",
  component: TableLayout,
};
