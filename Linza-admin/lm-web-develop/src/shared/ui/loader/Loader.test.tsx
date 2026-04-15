import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import Loader from "./index";

describe("Loader", () => {
  it("Default view", () => {
    const tree = render(<Loader size="m" />);
    expect(tree).toMatchSnapshot();
  });
});
