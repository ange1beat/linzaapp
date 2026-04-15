import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import UserChangePhonePage from "./index";

describe("UserChangePhonePage", () => {
  it("default view", () => {
    const tree = render(<UserChangePhonePage />);
    expect(tree).toMatchSnapshot();
  });
});
