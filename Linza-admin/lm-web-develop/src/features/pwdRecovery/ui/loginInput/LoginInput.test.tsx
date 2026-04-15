import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import LoginInput from "./index";

describe("LoginInput", () => {
  it("View default", () => {
    const tree = render(<LoginInput onSuccess={() => ""} />);

    expect(tree).toMatchSnapshot();
  });
});
