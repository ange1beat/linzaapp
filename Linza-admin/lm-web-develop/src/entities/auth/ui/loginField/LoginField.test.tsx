import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import LoginField from "./index";

describe("LoginField", () => {
  it("View default", () => {
    const tree = render(<LoginField onChange={() => {}} />);
    expect(tree).toMatchSnapshot();
  });
  it("View error", () => {
    const tree = render(
      <LoginField
        isError={true}
        errorMessage="Some error"
        onChange={() => {}}
      />,
    );
    expect(tree).toMatchSnapshot();
  });
  it("View disabled", () => {
    const tree = render(<LoginField disabled={true} onChange={() => {}} />);
    expect(tree).toMatchSnapshot();
  });
});
