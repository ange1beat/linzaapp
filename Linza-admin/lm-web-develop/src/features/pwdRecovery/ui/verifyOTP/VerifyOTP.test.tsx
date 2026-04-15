import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import VerifyOTP from "./index";

describe("VerifyOTP", () => {
  it("View default", () => {
    const tree = render(
      <VerifyOTP
        onSuccess={() => {}}
        onBack={() => {}}
        login="somemail@mail.ru"
        loginType="email"
      >
        <button>request code again</button>
      </VerifyOTP>,
    );
    expect(tree).toMatchSnapshot();
  });
});
