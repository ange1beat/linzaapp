import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import MenuWidget from "./index";

describe("MenuWidget", () => {
  it("View default", () => {
    const tree = render(<MenuWidget />);
    expect(tree).toMatchSnapshot();
  });
});
