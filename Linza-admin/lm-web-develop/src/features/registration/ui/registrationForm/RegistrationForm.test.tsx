import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import RegistrationForm from "./index";

describe("RegistrationForm", () => {
  it("view default", () => {
    const tree = render(
      <RegistrationForm
        className="test"
        onSuccess={() => {}}
        invitationId="228333"
      />,
    );
    expect(tree).toMatchSnapshot();
  });
});
