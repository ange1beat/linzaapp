import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import ProjectReportsDelete from "./index";

describe("ProjectReportsDelete", () => {
  it("Default view", () => {
    const tree = render(
      <ProjectReportsDelete
        isOpen={true}
        projectId="1"
        reports={[{ id: "1", name: "Test report 1" }]}
        onClose={() => null}
      />,
    );
    expect(tree).toMatchSnapshot();
  });

  it("Multiple view", () => {
    const tree = render(
      <ProjectReportsDelete
        isOpen={true}
        projectId="1"
        reports={[
          {
            id: "1",
            name: "Test report 1",
          },
          {
            id: "2",
            name: "Test report 2",
          },
          {
            id: "3",
            name: "Test report 3",
          },
          {
            id: "4",
            name: "Test report 4",
          },
          {
            id: "5",
            name: "Test report 5",
          },
          {
            id: "6",
            name: "Test report 6",
          },
          {
            id: "7",
            name: "Test report 7",
          },
        ]}
        onClose={() => null}
      />,
    );
    expect(tree).toMatchSnapshot();
  });
});
