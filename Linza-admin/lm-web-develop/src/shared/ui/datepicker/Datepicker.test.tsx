import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import Datepicker from "./index";

describe("Datepicker", () => {
  it("View default", () => {
    const tree = render(
      <Datepicker
        value={{
          startDate: new Date(2024, 1, 1),
          endDate: new Date(2024, 1, 10),
        }}
        onChange={() => {}}
      />,
    );
    expect(tree).toMatchSnapshot();
  });
});
