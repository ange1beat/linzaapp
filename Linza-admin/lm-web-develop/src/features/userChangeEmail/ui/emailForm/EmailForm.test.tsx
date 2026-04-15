import { describe, expect, it } from "vitest";

import { render } from "@/shared/tests";

import EmailForm from "./index";

describe("EmailForm", () => {
  it("View default", () => {
    const tree = render(<EmailForm onSuccess={() => {}} onCancel={() => {}} />);
    expect(tree).toMatchSnapshot();
  });
});
