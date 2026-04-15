import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import LabelMemberRole from "./index";

describe("Label", () => {
  it("supervisor", () => {
    const tree = render(<LabelMemberRole role="Supervisor" />);
    expect(tree).toMatchSnapshot();
  });
  it("user", () => {
    const tree = render(<LabelMemberRole role="User" />);
    expect(tree).toMatchSnapshot();
  });
});
