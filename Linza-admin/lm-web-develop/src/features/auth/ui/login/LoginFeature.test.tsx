import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import LoginFeature from "./index";

describe("LoginFeature", () => {
  it("View default", () => {
    const tree = render(
      <LoginFeature onSuccess={() => {}} onError={() => {}} />,
    );
    expect(tree).toMatchSnapshot();
  });
});
