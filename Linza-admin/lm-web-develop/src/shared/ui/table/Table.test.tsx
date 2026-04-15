import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import Table from "./index";

describe("Table", () => {
  it("default", () => {
    const tree = render(
      <Table
        data={[{ id: "1" }, { id: "2" }, { id: "3" }]}
        columns={[
          {
            id: "test-id1",
            name: "First Name",
            template: (item: { id: string }, index: number) => (
              <div>{index}</div>
            ),
          },
          {
            id: "test-id2",
            name: "Last Name",
            template: (item: { id: string }, index: number) => (
              <div>{index}</div>
            ),
          },
          {
            id: "test-id3",
            name: "Phone",
            template: (item: { id: string }, index: number) => (
              <div>{index}</div>
            ),
          },
        ]}
        isLoad={false}
      />,
    );
    expect(tree).toMatchSnapshot();
  });
});
