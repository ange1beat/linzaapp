import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import UserChangeTelegramPage from "./index";

describe("UserChangeTelegramPage", () => {
  it("default view", () => {
    const tree = render(<UserChangeTelegramPage />);
    expect(tree).toMatchSnapshot();
  });
});
