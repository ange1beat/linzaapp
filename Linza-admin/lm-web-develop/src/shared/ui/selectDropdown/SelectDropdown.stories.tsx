import React from "react";

import { Meta, StoryObj } from "@storybook/react";

import Button from "../button";
import List from "../list";

import SelectDropdown, { useSelectDropDown } from "./index";

const myItems = [
  { text: "list item 1", id: "1" },
  { text: "list item 2", id: "2" },
  { text: "list item 3", id: "3" },
  { text: "list item 4", id: "4" },
  { text: "list item 5", id: "5" },
  { text: "list item 6", id: "6" },
  { text: "list item 7", id: "7" },
];

const renderItem = (item: { id: string; text: string }) => {
  return <span>{item.text}</span>;
};

const meta: Meta<typeof SelectDropdown> = {
  component: SelectDropdown,
  title: "shared/SelectDropdown",
  argTypes: {},
};

export default meta;
type Story = StoryObj<typeof SelectDropdown>;

const ListTemplate: Story = {
  render: function MyComponent() {
    const { isOpen, onClose, onToggle, ref } = useSelectDropDown();
    return (
      <>
        <SelectDropdown
          isOpen={isOpen}
          onToggle={onToggle}
          switcher={<div>My custom switcher</div>}
          ref={ref}
        >
          <List
            items={myItems}
            renderItem={renderItem}
            isSelected={(item) => item.id === "3"}
            emptyMessage=""
            isLoad={false}
            onToggleSelect={() => {}}
            placeholder="Search"
            onSearch={() => {}}
            listHeight={224}
            itemHeight={36}
            view="outline"
          />
          <Button view="normal" onClick={onClose}>
            Close
          </Button>
        </SelectDropdown>
        <div>Something</div>
      </>
    );
  },
};

export const Empty = {
  ...ListTemplate,
  args: {
    items: [],
  },
};
