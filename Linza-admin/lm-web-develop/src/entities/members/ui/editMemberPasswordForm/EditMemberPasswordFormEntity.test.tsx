import { describe, it, expect } from "vitest";

import { render } from "../../../../shared/tests/instans";

import { EditMemberPasswordFormEntity } from "./index";

describe("Edit Member Password Form", () => {
  it("Test with data", () => {
    const tree = render(
      <EditMemberPasswordFormEntity
        memberId="1"
        onChange={() => {}}
        isOpen
        onSubmit={() => {}}
        isLoad
        errors={{ confirmPassword: "", newPassword: "error!" }}
        onCancel={() => {}}
      />,
    );
    expect(tree).toMatchSnapshot();
  });
});
