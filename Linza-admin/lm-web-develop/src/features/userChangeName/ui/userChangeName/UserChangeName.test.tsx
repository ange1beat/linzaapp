import { describe, expect, it } from "vitest";

import { render } from "@/shared/tests";

import UserChangeNameFeature from "./index";

describe("UserChangeNameFeature", () => {
  it("View default", () => {
    const tree = render(<UserChangeNameFeature />);
    expect(tree).toMatchSnapshot();
  });
});
