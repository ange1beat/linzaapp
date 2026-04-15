import { describe, expect, it } from "vitest";

import { render } from "@/shared/tests";

import PhoneOTPForm from "./index";

describe("PhoneOTPForm", () => {
  it("View default", () => {
    const tree = render(
      <PhoneOTPForm
        phone="+78005553535"
        onSuccess={() => {}}
        onBack={() => {}}
      />,
    );
    expect(tree).toMatchSnapshot();
  });
});
