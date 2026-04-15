import { Gear } from "@gravity-ui/icons";
import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";
import { Button } from "@/shared/ui";

import Layout from "./index";

const breadCrumbsItems = [
  {
    text: "Example",
    link: "/",
  },
];

describe("Layout", () => {
  it("View default", () => {
    const tree = render(<Layout items={breadCrumbsItems} />);
    expect(tree).toMatchSnapshot();
  });
  it("Layout with actions and content", () => {
    const tree = render(
      <Layout
        items={breadCrumbsItems}
        actions={
          <Button view="normal" size="m" iconLeft={<Gear />}>
            Settings
          </Button>
        }
      >
        Content
      </Layout>,
    );
    expect(tree).toMatchSnapshot();
  });
});
