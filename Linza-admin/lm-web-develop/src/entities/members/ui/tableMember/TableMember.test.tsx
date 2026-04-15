import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";
import { Button } from "@/shared/ui";

import TableMember from ".";

describe("Edit Member", () => {
  it("Test with data", () => {
    const tree = render(
      <TableMember
        rowActions={() => "..."}
        headerActions={<Button view="normal">Add user</Button>}
      />,
    );
    expect(tree).toMatchSnapshot();
  });
});
