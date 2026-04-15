import { StoryObj } from "@storybook/react";

import List from "./index";

const myItems = [
  { text: "list item 1", id: "1" },
  { text: "list item 2", id: "2" },
  { text: "list item 3", id: "3" },
  { text: "list item 4", id: "4" },
  { text: "list item 5", id: "5" },
  { text: "list item 6", id: "6" },
  { text: "list item 7", id: "7" },
];

const renderItem = (item: { id: string }) => {
  return <span>{item.id}</span>;
};

export const Default: StoryObj<typeof List> = {
  args: {
    emptyMessage: "1",
    placeholder: "Search",
    isLoad: false,
    isSelected: (item) => item.id === "2",
    items: myItems,
    renderItem: renderItem,
    itemHeight: 36,
    listHeight: 224,
  },
  argTypes: {
    view: {
      options: ["outline", "default"],
      control: { type: "radio" },
    },
  },
};

export default {
  title: "Shared/List",
  component: List,
};
