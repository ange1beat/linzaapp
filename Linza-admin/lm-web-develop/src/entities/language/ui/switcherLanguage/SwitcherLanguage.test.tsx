import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import SwitcherLanguage from "./index";

describe("SwitcherLanguage", () => {
  it("View default", () => {
    const tree = render(<SwitcherLanguage />);
    expect(tree).toMatchSnapshot();
  });
});
