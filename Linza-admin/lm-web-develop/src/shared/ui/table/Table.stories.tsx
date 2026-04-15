import React from "react";

import { StoryObj } from "@storybook/react";

import Table from "./index";

export const Default: StoryObj<typeof Table> = {
  args: {
    data: [{ id: "1" }, { id: "2" }, { id: "3" }],
    columns: [
      {
        id: "test-id1",
        name: "First Name",
        template: (item: { id: string }, index: number) => <div>{index}</div>,
      },
      {
        id: "test-id2",
        name: "Last Name",
        template: (item: { id: string }, index: number) => <div>{index}</div>,
      },
      {
        id: "test-id3",
        name: "Phone",
        template: (item: { id: string }, index: number) => <div>{index}</div>,
      },
    ],
    isLoad: false,
  },
};

export default {
  title: "Shared/Table",
  component: Table,
};
