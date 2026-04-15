import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import LoginPage from "./index";

describe("LoginPage", () => {
  it("default view", () => {
    const tree = render(<LoginPage />);
    expect(tree).toMatchSnapshot();
  });
});
