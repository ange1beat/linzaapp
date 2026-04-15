import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import MemberManagementProject from "./index";

describe("Add members to project", () => {
  it("default", () => {
    const tree = render(<MemberManagementProject memberId="1" />);
    expect(tree).toMatchSnapshot();
  });
});
