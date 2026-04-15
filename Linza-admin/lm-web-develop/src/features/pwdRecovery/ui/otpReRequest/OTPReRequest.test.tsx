import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import OTPReRequest from "./index";

describe("OTPReRequest", () => {
  it("View default", () => {
    const tree = render(
      <OTPReRequest login="test@mail.com" loginType="email" timer={5} />,
    );
    expect(tree).toMatchSnapshot();
  });
});
