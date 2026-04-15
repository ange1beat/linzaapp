import { describe, expect, it } from "vitest";

import { SourceType } from "@/entities/sources/models/types";
import { render } from "@/shared/tests";

import SourcesTypeEntity from "./index";

describe("SourcesTypeEntity", () => {
  it("Type web", () => {
    const tree = render(<SourcesTypeEntity type={SourceType.Web} />);
    expect(tree).toMatchSnapshot();
  });
  it("Type vk", () => {
    const tree = render(<SourcesTypeEntity type={SourceType.VK} />);
    expect(tree).toMatchSnapshot();
  });
  it("Type ok", () => {
    const tree = render(<SourcesTypeEntity type={SourceType.OK} />);
    expect(tree).toMatchSnapshot();
  });
  it("Type telegram", () => {
    const tree = render(<SourcesTypeEntity type={SourceType.Telegram} />);
    expect(tree).toMatchSnapshot();
  });
});
