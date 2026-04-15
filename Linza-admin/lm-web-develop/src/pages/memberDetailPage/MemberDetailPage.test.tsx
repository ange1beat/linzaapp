import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import MemberDetailPage from "./index";

describe("MemberDetailPage", () => {
  it("View default", () => {
    const tree = render(<MemberDetailPage />);
    expect(tree).toMatchSnapshot();
  });
});
