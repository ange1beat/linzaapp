import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import Skeleton from "./index";

describe("Skeleton", () => {
  it("View default", () => {
    const tree = render(
      <Skeleton isLoad={true} height={20}>
        some child
      </Skeleton>,
    );
    expect(tree).toMatchSnapshot();
  });
});
