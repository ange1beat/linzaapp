import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import UserChangeNamePage from "./index";

describe("UserChangeNamePage", () => {
  it("default view", () => {
    const tree = render(<UserChangeNamePage />);
    expect(tree).toMatchSnapshot();
  });
});
