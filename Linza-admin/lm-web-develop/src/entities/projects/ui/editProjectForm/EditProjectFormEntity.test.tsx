import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import EditProjectFormEntity from "./index";

describe("EditProjectFormEntity", () => {
  it("View default", () => {
    const tree = render(
      <EditProjectFormEntity
        errors={{ name: "", avatarUrl: "" }}
        isLoad={false}
        onChange={() => {}}
        onCancel={() => {}}
        data={{ name: "", avatarUrl: "" }}
        onSuccess={() => {}}
      />,
    );
    expect(tree).toMatchSnapshot();
  });
});
