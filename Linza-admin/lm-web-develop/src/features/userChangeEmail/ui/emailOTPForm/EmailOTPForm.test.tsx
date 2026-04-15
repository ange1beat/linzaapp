import { describe, expect, it } from "vitest";

import { render } from "@/shared/tests";

import EmailOTPForm from "./index";

describe("EmailOTPForm", () => {
  it("View default", () => {
    const tree = render(
      <EmailOTPForm
        email="example@mail.com"
        onSuccess={() => {}}
        onBack={() => {}}
      />,
    );
    expect(tree).toMatchSnapshot();
  });
});
