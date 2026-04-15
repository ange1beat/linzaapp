import { describe, it, expect } from "vitest";

import { render } from "../../../../shared/tests/instans";

import FoldersList from "./index";

describe("Folders List", () => {
  it("Test with data", () => {
    const tree = render(
      <FoldersList
        deleteAction={() => {}}
        projectId="1"
        addAction={<button>Add</button>}
      />,
    );
    expect(tree).toMatchSnapshot();
  });
});
