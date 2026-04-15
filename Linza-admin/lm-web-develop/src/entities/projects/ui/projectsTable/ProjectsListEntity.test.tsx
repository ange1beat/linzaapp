import { Ellipsis } from "@gravity-ui/icons";
import { Icon } from "@gravity-ui/uikit";
import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";
import { Favorite } from "@/shared/ui";

import ProjectsTable from "./index";

describe("ProjectsTable", () => {
  it("View default", () => {
    const tree = render(
      <ProjectsTable
        headerActions={<button>add project</button>}
        createdBy={(userId) => `userID: ${userId}`}
        rowActions={() => <Icon data={Ellipsis} />}
        favoriteProject={(isFavorite) => <Favorite isSelected={isFavorite} />}
      />,
    );
    expect(tree).toMatchSnapshot();
  });
});
