import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import ConfirmCodeForResetPasswordEntity from "./index";

describe("ConfirmCodeForResetPasswordEntity", () => {
  it("View default", () => {
    const tree = render(
      <ConfirmCodeForResetPasswordEntity
        onSubmit={() => {}}
        onBack={() => {}}
        loading={true}
        error="error"
        loginType="email"
      >
        <span>Test!</span>
      </ConfirmCodeForResetPasswordEntity>,
    );
    expect(tree).toMatchSnapshot();
  });
});
