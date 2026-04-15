import { describe, expect, it } from "vitest";

import { render } from "@/shared/tests";

import ChangeEmail from "./index";

describe("ChangeEmail", () => {
  it("View default", () => {
    const tree = render(<ChangeEmail />);
    expect(tree).toMatchSnapshot();
  });
});
