import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import InputPassword from "./index";

describe("InputPassword", () => {
  it("view default", () => {
    const tree = render(<InputPassword value="" onChange={() => ""} />);
    expect(tree).toMatchSnapshot();
  });

  it("render error input", () => {
    const tree = render(
      <InputPassword
        value=""
        onChange={() => ""}
        isError
        errorMessage="Error"
      />,
    );
    expect(tree).toMatchSnapshot();
  });
});
