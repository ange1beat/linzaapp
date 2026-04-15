import { describe, expect, it } from "vitest";

import { render } from "@/shared/tests";

import UserPasswordChange from "./index";

describe("UserPasswordChangeFeature", () => {
  it("View default", () => {
    const tree = render(<UserPasswordChange />);
    expect(tree).toMatchSnapshot();
  });
});
