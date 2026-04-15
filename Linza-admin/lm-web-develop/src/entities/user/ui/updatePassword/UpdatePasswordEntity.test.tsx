import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import UpdatePasswordEntity from "./index";

describe("UpdatePasswordEntity", () => {
  it("View default", () => {
    const tree = render(
      <UpdatePasswordEntity
        onSubmit={() => {}}
        onChange={() => {}}
        errors={{ currentPassword: "", newPassword: "", confirmPassword: "" }}
        isLoad={false}
      />,
    );
    expect(tree).toMatchSnapshot();
  });
});
