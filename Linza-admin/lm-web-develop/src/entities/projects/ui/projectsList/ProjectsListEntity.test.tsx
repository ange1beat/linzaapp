import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import ProjectsListEntity from "./index";

describe("ProjectsListEntity", () => {
  it("View default", () => {
    const tree = render(
      <ProjectsListEntity
        onDeselect={() => {}}
        onSelect={() => {}}
        selected={["1"]}
        isDisabled={false}
      />,
    );
    expect(tree).toMatchSnapshot();
  });
});
