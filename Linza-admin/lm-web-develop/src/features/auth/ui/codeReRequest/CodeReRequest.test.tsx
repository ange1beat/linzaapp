import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import CodeReRequest from "./index";

describe("CodeReRequest", () => {
  it("View default", () => {
    const tree = render(<CodeReRequest loginType="email" stateToken="stateToken" />);
    expect(tree).toMatchSnapshot();
  });
});
