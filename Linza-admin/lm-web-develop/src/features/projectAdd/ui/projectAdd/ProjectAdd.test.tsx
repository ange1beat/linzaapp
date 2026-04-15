import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import ProjectAdd from "./index";

describe("ProjectAdd", () => {
  it("Default view", () => {
    const tree = render(
      <ProjectAdd isOpen={true} onClose={() => null} onSuccess={() => null} />,
    );
    expect(tree).toMatchSnapshot();
  });
});
