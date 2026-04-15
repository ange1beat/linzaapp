import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import ProjectDetailsPage from "./index";

describe("ProjectDetailsPage", () => {
  it("View default", () => {
    const tree = render(<ProjectDetailsPage />);
    expect(tree).toMatchSnapshot();
  });
});
