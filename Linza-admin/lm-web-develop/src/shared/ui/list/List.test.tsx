import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import List from "./index";

const renderItem = (item: { id: string }) => {
  return <span>{item.id}</span>;
};

describe("List testing", () => {
  it("Default", () => {
    const tree = render(
      <List
        items={[
          { text: "list item 1", id: "1" },
          { text: "list item 2", id: "2" },
          { text: "list item 3", id: "3" },
        ]}
        renderItem={renderItem}
        isSelected={(item) => item.id === "3"}
        emptyMessage=""
        isLoad={false}
        onToggleSelect={() => {}}
        placeholder="Search"
        onSearch={() => {}}
        listHeight={32}
        itemHeight={244}
      />,
    );
    expect(tree).toMatchSnapshot();
  });
});
