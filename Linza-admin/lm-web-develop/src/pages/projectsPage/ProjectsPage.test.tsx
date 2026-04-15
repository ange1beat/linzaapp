import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import ProjectsPage from "./index";

describe("ProjectsPage", () => {
  it("view default", () => {
    const tree = render(<ProjectsPage />);
    expect(tree).toMatchSnapshot();
  });
});
