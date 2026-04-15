import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import MembersListEntity from "./index";

describe("MembersList default", () => {
  it("Test with data", () => {
    const tree = render(
      <MembersListEntity
        selected={["1"]}
        onSelect={() => {}}
        onDeselect={() => {}}
      />,
    );
    expect(tree).toMatchSnapshot();
  });
});
