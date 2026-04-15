import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import UserChangeEmailPage from "./index";

describe("UserChangeEmailPage", () => {
  it("default view", () => {
    const tree = render(<UserChangeEmailPage />);
    expect(tree).toMatchSnapshot();
  });
});
