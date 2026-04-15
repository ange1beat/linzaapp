import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import DeleteProject from "./index";

describe("DeleteProject", () => {
  it("Default view", () => {
    const tree = render(
      <DeleteProject
        isOpen={true}
        project={{ id: "12", name: "Some project" }}
        onClose={() => null}
      />,
    );
    expect(tree).toMatchSnapshot();
  });
});
