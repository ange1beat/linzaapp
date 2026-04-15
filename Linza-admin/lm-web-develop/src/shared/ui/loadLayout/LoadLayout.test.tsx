import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import LoadLayout from "./index";

describe("LoadLayout", () => {
  it("view default", () => {
    const tree = render(
      <LoadLayout isLoad={true} size="l">
        <div>here must be some child</div>
      </LoadLayout>,
    );
    expect(tree).toMatchSnapshot();
  });
});
