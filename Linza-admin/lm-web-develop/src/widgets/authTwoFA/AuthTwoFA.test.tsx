import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import AuthTwoFA from "./index";

describe("AuthTwoFA work", () => {
  it("View default email", () => {
    const tree = render(
      <AuthTwoFA
        onSuccess={() => {}}
        onError={() => {}}
        stateToken={"3332222"}
        onBack={() => {}}
        loginType={"email"}
        isLoading={false}
      />,
    );
    expect(tree).toMatchSnapshot();
  });

  it("View default phone", () => {
    const tree = render(
      <AuthTwoFA
        onSuccess={() => {}}
        onError={() => {}}
        stateToken={"3332222"}
        onBack={() => {}}
        loginType={"phone"}
        isLoading={false}
      />,
    );
    expect(tree).toMatchSnapshot();
  });
});
