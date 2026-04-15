import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import Timer from "./index";

describe("Timer", () => {
  it("with minutes and seconds", () => {
    const tree = render(
      <Timer
        timer={125}
        actions={() => ""}
        template={(val) => `Request again in ${val}`}
        countDownEndText="Requested again to"
        isLoading={true}
      />,
    );
    expect(tree).toMatchSnapshot();
  });

  it("with seconds only", () => {
    const tree = render(
      <Timer
        timer={35}
        actions={() => ""}
        template={(val) => `Request again in ${val}`}
        countDownEndText="Requested again to"
        isLoading={false}
      />,
    );
    expect(tree).toMatchSnapshot();
  });
});
