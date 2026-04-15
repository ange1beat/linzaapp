import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import MenuLayout from "./index";

describe("MenuLayout", () => {
  it("view default", () => {
    const tree = render(
      <MenuLayout>
        <div>here must be some children</div>
      </MenuLayout>,
    );
    expect(tree).toMatchSnapshot();
  });
});
