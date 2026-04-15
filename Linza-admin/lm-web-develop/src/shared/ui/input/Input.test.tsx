import { Smartphone } from "@gravity-ui/icons";
import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import Input from "./index";

describe("Checked Input States", () => {
  it("default state", () => {
    const tree = render(<Input value="" onChange={() => ""} size="xl" />);
    expect(tree).toMatchSnapshot();
  });

  it("state with value", () => {
    const tree = render(
      <Input value="test value" onChange={() => ""} size="xl" />,
    );
    expect(tree).toMatchSnapshot();
  });

  it("state with value and error", () => {
    const tree = render(
      <Input
        value="test value"
        onChange={() => ""}
        isError
        errorMessage="Error!"
      />,
    );
    expect(tree).toMatchSnapshot();
  });

  it("state with right content", () => {
    const tree = render(
      <Input
        value="test value"
        onChange={() => ""}
        rightContent={<Smartphone />}
      />,
    );
    expect(tree).toMatchSnapshot();
  });
});
