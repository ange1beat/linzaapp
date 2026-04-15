import { describe, expect, it } from "vitest";

import { render } from "@/shared/tests";

import ProjectChangeName from "./index";

describe("ProjectChangeName", () => {
  it("View default", () => {
    const tree = render(
      <ProjectChangeName project={{ id: "1", name: "test project" }} />,
    );
    expect(tree).toMatchSnapshot();
  });
});
