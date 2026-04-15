import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import ResetPasswordWidget from "./index";

describe("ResetPasswordWidget", () => {
  it("View default", () => {
    const tree = render(<ResetPasswordWidget />);
    expect(tree).toMatchSnapshot();
  });
});
