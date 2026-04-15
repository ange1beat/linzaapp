import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";
import { MembersPage } from "@/pages/index";

describe("MembersPage", () => {
  it("view default", () => {
    const tree = render(<MembersPage />);
    expect(tree).toMatchSnapshot();
  });
});
