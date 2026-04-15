import { describe, it, expect } from "vitest";

import { render } from "../../../../shared/tests/instans";

import FolderItem from "./index";

describe("Folder Item", () => {
  it("Test with data", () => {
    const tree = render(
      <FolderItem
        folder={{ id: "1", name: "Folder 01.01.2024" }}
        onDelete={() => {}}
        projectId="1"
      />,
    );
    expect(tree).toMatchSnapshot();
  });
});
