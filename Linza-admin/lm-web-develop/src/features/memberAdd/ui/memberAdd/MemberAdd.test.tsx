import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import MemberAdd from "./index";

describe("Add Member", () => {
  it("default", () => {
    const tree = render(
      <MemberAdd
        onSuccess={() => {}}
        onCancel={() => {}}
        children={<button />}
      />,
    );
    expect(tree).toMatchSnapshot();
  });
});
