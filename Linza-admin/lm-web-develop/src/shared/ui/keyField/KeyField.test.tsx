import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import KeyField from "./index";

describe("Checked KeyField States", () => {
  it("default state", () => {
    const tree = render(<KeyField onChange={() => ""} />);
    expect(tree).toMatchSnapshot();
  });

  it("state with error", () => {
    const tree = render(
      <KeyField onChange={() => ""} isError errorMessage="Error!" />,
    );
    expect(tree).toMatchSnapshot();
  });

  it("disabled", () => {
    const tree = render(<KeyField onChange={() => ""} disabled />);

    expect(tree).toMatchSnapshot();
  });
});
