import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import Spin from "./index";

describe("Spin", () => {
  it("Default view", () => {
    const tree = render(<Spin size="m" />);
    expect(tree).toMatchSnapshot();
  });
});
