import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import ResetPasswordSuccessPage from "./index";

describe("ResetPasswordSuccessPage", () => {
  it("default view", () => {
    const tree = render(<ResetPasswordSuccessPage />);
    expect(tree).toMatchSnapshot();
  });
});
