import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import InputConfirm from "./index";

describe("InputConfirm", () => {
  it("default view", () => {
    const tree = render(
      <InputConfirm value="input with confirm buttons" onApply={() => ""} />,
    );
    expect(tree).toMatchSnapshot();
  });
});
