import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import ModalWindow from "./index";

describe("ModalWindow", () => {
  it("Open modal view", () => {
    const tree = render(
      <ModalWindow title="Test modal title" onClose={() => {}} isOpen={true}>
        Test
      </ModalWindow>,
    );
    expect(tree).toMatchSnapshot();
  });
});
