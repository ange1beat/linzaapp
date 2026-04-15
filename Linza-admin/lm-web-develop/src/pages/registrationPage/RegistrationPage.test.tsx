import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import RegistrationPage from "./index";

describe("Registration Page", () => {
  it("default view", () => {
    const tree = render(<RegistrationPage />);
    expect(tree).toMatchSnapshot();
  });
});
