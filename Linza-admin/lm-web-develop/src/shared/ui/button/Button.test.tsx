import { Gear } from "@gravity-ui/icons";
import { Icon } from "@gravity-ui/uikit";
import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import Button from "./index";

describe("Button", () => {
  it("View action", () => {
    const tree = render(
      <Button view="action" onClick={() => ""}>
        Test
      </Button>,
    );
    expect(tree).toMatchSnapshot();
  });

  it("View normal", () => {
    const tree = render(
      <Button view="normal" onClick={() => ""}>
        Test
      </Button>,
    );
    expect(tree).toMatchSnapshot();
  });

  it("Disabled", () => {
    const tree = render(
      <Button view="normal" onClick={() => ""} disabled>
        Test
      </Button>,
    );
    expect(tree).toMatchSnapshot();
  });

  it("Loading", () => {
    const tree = render(
      <Button view="normal" onClick={() => ""} loading>
        Test
      </Button>,
    );
    expect(tree).toMatchSnapshot();
  });

  it("With Left icon", () => {
    const tree = render(
      <Button view="normal" onClick={() => ""} iconLeft={<Icon data={Gear} />}>
        Test
      </Button>,
    );
    expect(tree).toMatchSnapshot();
  });

  it("With Right icon", () => {
    const tree = render(
      <Button view="normal" onClick={() => ""} iconRight={<Icon data={Gear} />}>
        Test
      </Button>,
    );
    expect(tree).toMatchSnapshot();
  });
});
