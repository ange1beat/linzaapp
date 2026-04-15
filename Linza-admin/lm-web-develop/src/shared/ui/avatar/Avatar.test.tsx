import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import Avatar from "./index";

describe("Avatar", () => {
  it("View default", () => {
    const tree = render(
      <Avatar avatar={""} defaultAva={""} onChange={(ava) => ava} />,
    );
    expect(tree).toMatchSnapshot();
  });
  it("Avatar exist", () => {
    const tree = render(
      <Avatar
        defaultAva={""}
        avatar={"https://go-link.ru/mBLDV"}
        onChange={(ava) => ava}
      />,
    );
    expect(tree).toMatchSnapshot();
  });
});
