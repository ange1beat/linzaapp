import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import MenuProjectItem from "./index";

describe("MenuProjectItem", () => {
  it("View default", () => {
    const tree = render(<MenuProjectItem />);
    expect(tree).toMatchSnapshot();
  });
  it("View with avatarUrl", () => {
    const tree = render(<MenuProjectItem avatarUrl="/www.example.com/213" />);
    expect(tree).toMatchSnapshot();
  });
});
