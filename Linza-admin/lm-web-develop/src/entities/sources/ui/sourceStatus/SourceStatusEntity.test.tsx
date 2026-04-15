import { describe, expect, it } from "vitest";

import { SourceExecutionStatus } from "@/entities/sources/models/types";
import { render } from "@/shared/tests";

import SourceStatusEntity from "./index";

describe("SourceStatusEntity", () => {
  it("Planned status", () => {
    const tree = render(
      <SourceStatusEntity executionStatus={SourceExecutionStatus.Planned} />,
    );
    expect(tree).toMatchSnapshot();
  });
  it("In progress status", () => {
    const tree = render(
      <SourceStatusEntity executionStatus={SourceExecutionStatus.InProgress} />,
    );
    expect(tree).toMatchSnapshot();
  });
  it("Stopped status", () => {
    const tree = render(
      <SourceStatusEntity executionStatus={SourceExecutionStatus.Stopped} />,
    );
    expect(tree).toMatchSnapshot();
  });
  it("Not configure status", () => {
    const tree = render(
      <SourceStatusEntity
        executionStatus={SourceExecutionStatus.NotConfigure}
      />,
    );
    expect(tree).toMatchSnapshot();
  });
});
