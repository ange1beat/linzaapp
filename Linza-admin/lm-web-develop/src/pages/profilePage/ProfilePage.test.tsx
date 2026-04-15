import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import ProfilePage from "./index";

describe("ProfilePage", () => {
  it("View default", () => {
    const tree = render(<ProfilePage />);
    expect(tree).toMatchSnapshot();
  });
});
