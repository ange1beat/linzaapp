import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import InputSearch from "./index";

describe("InputSearch", () => {
  it("view default", () => {
    const tree = render(<InputSearch onSearchChange={() => ""} />);
    expect(tree).toMatchSnapshot();
  });

  it("render error input", () => {
    const tree = render(
      <InputSearch onSearchChange={() => ""} isError errorMessage="Error" />,
    );
    expect(tree).toMatchSnapshot();
  });
});
