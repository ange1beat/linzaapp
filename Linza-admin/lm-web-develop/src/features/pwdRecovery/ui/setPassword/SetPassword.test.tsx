import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import SetPassword from "./index";

describe("SetPassword", () => {
  it("View default", () => {
    const tree = render(
      <SetPassword
        onClick={() => {}}
        onError={() => {}}
        onSuccess={() => {}}
        recoveryToken="token"
      />,
    );
    expect(tree).toMatchSnapshot();
  });
});
