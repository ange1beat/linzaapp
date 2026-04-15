import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import RegistrationSuccessPage from "./index";

describe("Registration Success Page", () => {
  it("default view", () => {
    const tree = render(<RegistrationSuccessPage />);
    expect(tree).toMatchSnapshot();
  });
});
