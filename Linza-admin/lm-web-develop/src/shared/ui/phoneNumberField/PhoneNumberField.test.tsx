import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import PhoneNumberField from "./index";

describe("PhoneNumberField", () => {
  it("Default", () => {
    const tree = render(
      <PhoneNumberField
        isError={false}
        errorMessage={"error"}
        placeholder={"8 800 555 35 35"}
        onChange={() => {}}
      />,
    );
    expect(tree).toMatchSnapshot();
  });
});
