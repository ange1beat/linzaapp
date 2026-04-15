import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import ProjectMembersTable from "./index";

describe("ProjectMembersTable", () => {
  it("Default", () => {
    const tree = render(
      <ProjectMembersTable
        projectId="1"
        rowActions={() => "..."}
        headActions={<>Add user</>}
      />,
    );
    expect(tree).toMatchSnapshot();
  });
});
