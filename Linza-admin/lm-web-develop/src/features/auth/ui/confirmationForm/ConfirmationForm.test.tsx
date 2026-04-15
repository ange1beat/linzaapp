import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import ConfirmationForm from "./index";

describe("ConfirmationForm", () => {
  it("Form without default value", () => {
    const defaultLink = render(
      <ConfirmationForm stateToken="" onSuccess={() => {}} onError={() => {}}>
        <p>child!</p>
      </ConfirmationForm>,
    );
    expect(defaultLink).toMatchSnapshot();
  });

  it("Form with default value", () => {
    const defaultLink = render(
      <ConfirmationForm
        stateToken="666666"
        onSuccess={() => () => {}}
        onError={() => () => {}}
      >
        <p>child!</p>
      </ConfirmationForm>,
    );
    expect(defaultLink).toMatchSnapshot();
  });
});
