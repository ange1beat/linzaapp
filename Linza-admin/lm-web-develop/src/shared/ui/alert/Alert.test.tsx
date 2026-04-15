import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import Alert from "./alert";

describe("Alert", () => {
  it("View success", () => {
    const tree = render(
      <Alert
        id={1}
        options={{
          title: "Success",
          theme: "success",
          message: "Success message",
        }}
      />,
    );
    expect(tree).toMatchSnapshot();
  });

  it("View warning", () => {
    const tree = render(
      <Alert
        id={2}
        options={{
          title: "Warning",
          theme: "warning",
          message: "Warning message",
        }}
      />,
    );
    expect(tree).toMatchSnapshot();
  });

  it("View danger", () => {
    const tree = render(
      <Alert
        id={3}
        options={{
          title: "Danger",
          theme: "danger",
          message: "Danger message",
        }}
      />,
    );
    expect(tree).toMatchSnapshot();
  });
});
