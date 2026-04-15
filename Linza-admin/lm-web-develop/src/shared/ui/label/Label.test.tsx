import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import Label from "./index";

describe("Label", () => {
  it("default", () => {
    const tree = render(
      <Label theme="danger" className="label">
        Hello World!
      </Label>,
    );
    expect(tree).toMatchSnapshot();
  });
});
