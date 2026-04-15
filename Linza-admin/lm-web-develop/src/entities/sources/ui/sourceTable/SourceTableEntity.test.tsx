import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import SourceTableEntity from "./index";

describe("SourceTableEntity", () => {
  it("Type web", () => {
    const tree = render(
      <SourceTableEntity
        actions={() => <>...</>}
        headerActions={<div>...</div>}
        statusControl={() => <>...</>}
      />,
    );
    expect(tree).toMatchSnapshot();
  });
});
