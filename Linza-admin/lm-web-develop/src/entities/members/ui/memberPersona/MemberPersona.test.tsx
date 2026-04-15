import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import MemberPersona from "./index";

describe("MemberPersona", () => {
  it("default", () => {
    const tree = render(<MemberPersona memberId="1" />);
    expect(tree).toMatchSnapshot();
  });
});
