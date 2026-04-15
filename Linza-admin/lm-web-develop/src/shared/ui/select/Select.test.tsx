import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import Select from "./index";

describe("Select", () => {
  it("default", () => {
    const tree = render(
      <Select
        placeholder={"placeholder"}
        value={"value"}
        options={[{ value: "newValue", label: "newLabel" }]}
        onChange={() => {}}
      />,
    );
    expect(tree).toMatchSnapshot();
  });
});
