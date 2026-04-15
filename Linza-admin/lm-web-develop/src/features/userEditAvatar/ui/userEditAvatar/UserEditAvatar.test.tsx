import { describe, expect, it } from "vitest";

import { render } from "@/shared/tests";

import UserEditAvatar from "./index";

describe("UserChangeTelegram", () => {
  it("View Default", () => {
    const tree = render(<UserEditAvatar avatar="image.jpg" />);
    expect(tree).toMatchSnapshot();
  });
});
