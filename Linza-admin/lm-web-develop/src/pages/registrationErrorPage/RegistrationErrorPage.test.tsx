import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import RegistrationErrorPage from "./index";

describe("Registration Error Page", () => {
  it("default view", () => {
    const tree = render(<RegistrationErrorPage />);
    expect(tree).toMatchSnapshot();
  });
});
