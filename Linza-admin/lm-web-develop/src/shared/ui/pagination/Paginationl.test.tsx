import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import Pagination from "./index";

describe("Pagination", () => {
  it("default", () => {
    const tree = render(
      <Pagination
        total={40}
        page={1}
        pageSize={5}
        pageSizeOptions={[5, 10, 15, 20]}
        onUpdate={() => {}}
      />,
    );
    expect(tree).toMatchSnapshot();
  });
});
