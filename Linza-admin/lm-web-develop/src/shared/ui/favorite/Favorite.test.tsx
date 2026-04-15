import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import Favorite from "./index";

describe("Favorite", () => {
  it("View default", () => {
    const tree = render(<Favorite isSelected={false} />);
    expect(tree).toMatchSnapshot();
  });
  it("View selected", () => {
    const tree = render(<Favorite isSelected={true} />);
    expect(tree).toMatchSnapshot();
  });
});
