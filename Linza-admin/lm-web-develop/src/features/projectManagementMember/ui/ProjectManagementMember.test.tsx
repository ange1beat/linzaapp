import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import ProjectManagementMember from "./index";

describe("Project Management Member", () => {
  it("default", () => {
    const tree = render(<ProjectManagementMember projectId="1" />);
    expect(tree).toMatchSnapshot();
  });
});
