import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import UserChangePasswordPage from "./index";

describe("UserChangePasswordPage", () => {
  it("default view", () => {
    const tree = render(<UserChangePasswordPage />);
    expect(tree).toMatchSnapshot();
  });
});
