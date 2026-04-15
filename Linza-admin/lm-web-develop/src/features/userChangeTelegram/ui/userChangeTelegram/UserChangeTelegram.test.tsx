import { describe, expect, it } from "vitest";

import { render } from "@/shared/tests";

import UserChangeTelegram from "./index";

describe("UserChangeTelegram", () => {
  it("View default", () => {
    const tree = render(<UserChangeTelegram />);
    expect(tree).toMatchSnapshot();
  });
});
