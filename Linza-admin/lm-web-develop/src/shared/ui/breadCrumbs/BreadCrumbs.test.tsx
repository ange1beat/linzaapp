import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import BreadCrumbs from "./index";

describe("BreadCrumbs", () => {
  it("View default", () => {
    const tree = render(<BreadCrumbs items={[{ text: "First", link: "/" }]} />);
    expect(tree).toMatchSnapshot();
  });
  it("Multiple", () => {
    const tree = render(
      <BreadCrumbs
        items={[
          { text: "First", link: "/" },
          { text: "Second", link: "/" },
        ]}
      />,
    );
    expect(tree).toMatchSnapshot();
  });
});
