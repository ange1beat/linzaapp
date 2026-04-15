import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import BaseLayout from "./index";

describe("BaseLayout", () => {
  it("view default", () => {
    const tree = render(
      <BaseLayout>
        <div>here must be some children</div>
      </BaseLayout>,
    );
    expect(tree).toMatchSnapshot();
  });
});
