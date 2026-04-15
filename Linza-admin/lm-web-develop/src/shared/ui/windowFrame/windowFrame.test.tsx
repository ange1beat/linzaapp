import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import WindowFrame from "./index";

describe("Check window for login form", () => {
  it("test window", () => {
    const tree = render(
      <WindowFrame title="test title">
        <div>here must be some children</div>
      </WindowFrame>,
    );
    expect(tree).toMatchSnapshot();
  });
});
