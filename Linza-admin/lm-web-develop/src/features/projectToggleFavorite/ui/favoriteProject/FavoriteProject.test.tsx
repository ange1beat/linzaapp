import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import FavoriteProject from "./index";

describe("FavoriteProject", () => {
  it("Project in favorite", () => {
    const tree = render(<FavoriteProject isFavorite={true} projectId="1" />);
    expect(tree).toMatchSnapshot();
  });
  it("Project is not in favorites", () => {
    const tree = render(<FavoriteProject isFavorite={false} projectId="1" />);
    expect(tree).toMatchSnapshot();
  });
});
