import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import ProjectFolders from "./index";

describe("Project Folders Page", () => {
  it("View default", () => {
    const tree = render(<ProjectFolders />);
    expect(tree).toMatchSnapshot();
  });
});
