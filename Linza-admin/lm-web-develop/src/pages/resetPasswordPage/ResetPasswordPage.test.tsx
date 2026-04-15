import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import ResetPasswordPage from "./index";

describe("ResetPasswordPage", () => {
  it("default view", () => {
    const tree = render(<ResetPasswordPage />);
    expect(tree).toMatchSnapshot();
  });
});
