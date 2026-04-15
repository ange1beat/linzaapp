import { describe, it, expect } from "vitest";

import { USER_ROLES } from "@/shared/config";
import { render } from "@/shared/tests";

import MemberRoleSelect from "./index";

describe("MemberRoleSelect", () => {
  it("default", () => {
    const tree = render(
      <MemberRoleSelect
        member={{
          id: "1",
          roles: [USER_ROLES.Supervisor],
        }}
      />,
    );
    expect(tree).toMatchSnapshot();
  });
});
