import { describe, expect, it } from "vitest";

import { render } from "@/shared/tests";

import FolderDelete from "./index";

describe("Delete Folder", () => {
  it("Default view", () => {
    const tree = render(
      <FolderDelete
        isOpen={true}
        folder={{ id: "1", name: "Folder 01.01.2024" }}
        projectId={"1"}
        onCancel={() => {}}
      />,
    );
    expect(tree).toMatchSnapshot();
  });
});
