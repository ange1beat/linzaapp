import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests/instans";

import ProjectChangeAvatar from "./index";

describe("ProjectChangeAvatar", () => {
  it("With avatar view", () => {
    const tree = render(
      <ProjectChangeAvatar
        project={{
          id: "2",
          avatarUrl:
            "https://robohash.org/optioofficiabeatae.png?size=50x50&set=set1",
        }}
      />,
    );
    expect(tree).toMatchSnapshot();
  });

  it("Without avatar view", () => {
    const tree = render(
      <ProjectChangeAvatar
        project={{
          id: "2",
          avatarUrl: null,
        }}
      />,
    );
    expect(tree).toMatchSnapshot();
  });
});
