import { describe, expect, it } from "vitest";

import { SourceLastResult } from "@/entities/sources/models/types";
import { render } from "@/shared/tests";

import SourcesResultEntity from "./index";

describe("SourcesResultEntity", () => {
  it("Success status", () => {
    const tree = render(
      <SourcesResultEntity status={SourceLastResult.Success} />,
    );
    expect(tree).toMatchSnapshot();
  });
  it("Error status", () => {
    const tree = render(
      <SourcesResultEntity status={SourceLastResult.Error} />,
    );
    expect(tree).toMatchSnapshot();
  });
  it("Without status", () => {
    const tree = render(<SourcesResultEntity />);
    expect(tree).toMatchSnapshot();
  });
});
