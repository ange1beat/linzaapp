import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import TableLayout from "./index";

describe("TableLayout", () => {
  it("default", () => {
    const tree = render(
      <TableLayout>
        <TableLayout.Header>search and filters</TableLayout.Header>
        <TableLayout.Body>table</TableLayout.Body>
        <TableLayout.Footer>Pagination</TableLayout.Footer>
      </TableLayout>,
    );
    expect(tree).toMatchSnapshot();
  });
});
