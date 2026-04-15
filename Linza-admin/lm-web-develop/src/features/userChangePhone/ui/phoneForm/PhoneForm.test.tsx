import { describe, expect, it } from "vitest";

import { render } from "@/shared/tests";

import PhoneForm from "./index";

describe("PhoneForm", () => {
  it("View default", () => {
    const tree = render(<PhoneForm onSuccess={() => {}} onCancel={() => {}} />);
    expect(tree).toMatchSnapshot();
  });
});
