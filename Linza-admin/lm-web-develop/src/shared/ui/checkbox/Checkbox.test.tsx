import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import Checkbox from "./index";

describe("Checkbox", () => {
  it("Checked state", () => {
    const tree = render(<Checkbox checked onChange={() => {}} size="m" />);
    expect(tree).toMatchSnapshot();
  });

  it("Unchecked State", () => {
    const tree = render(
      <Checkbox checked={false} onChange={() => {}} size={"m"} />,
    );
    expect(tree).toMatchSnapshot();
  });
});
