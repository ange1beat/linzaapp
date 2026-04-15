import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import UserMenuItem from "./index";

describe("UserMenuItem", () => {
  it("View default", () => {
    const tree = render(
      <UserMenuItem
        isSelected={false}
        onClick={() => {}}
        onMouseDown={() => {}}
        onTouchStart={() => {}}
      />,
    );
    expect(tree).toMatchSnapshot();
  });
});
