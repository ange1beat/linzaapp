import { renderHook } from "@testing-library/react";
import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

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

describe("SelectDropdown", () => {
  it("default view list", () => {
    const { result } = renderHook(() => useSelectDropDown());
    const tree = render(
      <SelectDropdown
        isOpen={result.current.isOpen}
        onToggle={result.current.onToggle}
        switcher={<div>My custom switcher</div>}
        ref={result.current.ref}
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
        />
      </SelectDropdown>,
    );
    expect(tree).toMatchSnapshot();
  });
});
