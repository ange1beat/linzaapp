import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import TriggerSwitcherNotAuth from "./index";

describe("TriggerSwitcherNotAuth", () => {
  it("View default", () => {
    const tree = render(<TriggerSwitcherNotAuth />);
    expect(tree).toMatchSnapshot();
  });
});
