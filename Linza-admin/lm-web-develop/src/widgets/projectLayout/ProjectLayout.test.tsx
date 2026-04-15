import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import ProjectLayout from "./index";

describe("ProjectLayout", () => {
  it("dashboard view", () => {
    const tree = render(
      <ProjectLayout projectId="1" currentTab="dashboard">
        dashboard
      </ProjectLayout>,
    );
    expect(tree).toMatchSnapshot();
  });
  it("folders view", () => {
    const tree = render(
      <ProjectLayout projectId="1" currentTab="folders">
        folders
      </ProjectLayout>,
    );
    expect(tree).toMatchSnapshot();
  });
  it("reports view", () => {
    const tree = render(
      <ProjectLayout projectId="1" currentTab="reports">
        reports
      </ProjectLayout>,
    );
    expect(tree).toMatchSnapshot();
  });
  it("documents view", () => {
    const tree = render(
      <ProjectLayout projectId="1" currentTab="documents">
        documents
      </ProjectLayout>,
    );
    expect(tree).toMatchSnapshot();
  });
  it("sources view", () => {
    const tree = render(
      <ProjectLayout projectId="1" currentTab="sources">
        sources
      </ProjectLayout>,
    );
    expect(tree).toMatchSnapshot();
  });
  it("projectMembers view", () => {
    const tree = render(
      <ProjectLayout projectId="1" currentTab="members">
        members
      </ProjectLayout>,
    );
    expect(tree).toMatchSnapshot();
  });
});
