import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import OTPForm from "./index";

describe("OTPFormWithResend", () => {
  it("Default view", () => {
    const tree = render(
      <OTPForm
        isLoading={false}
        onSubmit={() => Promise.resolve()}
        onBack={() => {}}
      >
        <button>Request again</button>
      </OTPForm>,
    );
    expect(tree).toMatchSnapshot();
  });
});
