import { describe, expect, it } from "vitest";

import { render } from "@/shared/tests";

import ChangePhone from "./index";

describe("ChangePhone", () => {
  it("View default", () => {
    const tree = render(<ChangePhone />);
    expect(tree).toMatchSnapshot();
  });
});
